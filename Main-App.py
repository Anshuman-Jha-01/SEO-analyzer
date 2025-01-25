import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import string
import plotly.graph_objects as go

# Function to clean and tokenize text
def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
    text = re.sub(r'\d+', '', text)  # Remove digits
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    text = text.lower()  # Convert to lowercase
    return text

# Function to calculate the SEO score based on new factors
def calculate_seo_score(seo_report, bounce_rate, time_on_page, pages_per_session):
    score = 0
    max_score = 100  # Ensure the score is out of 100

    # Meta titles and descriptions (weight: 20%)
    title_info = seo_report["result"]["title"]
    meta_info = seo_report["result"]["meta_description"]
    if title_info["found"] == "Found" and title_info["length"] > 0:
        score += 5  # 10 points for meta title being present and valid
    if meta_info["found"] == "Found" and meta_info["length"] > 0:
        score += 10  # 10 points for meta description being present and valid

    # Internal links and broken links (weight: 15%)
    links_summary = seo_report["result"]["links_summary"]
    total_links = links_summary["total_links"]
    if total_links > 0:
        score += 10  # 10 points for having internal/external links
        if links_summary["nofollow_count"] == 0:  # Deduct if there are broken links
            score += 5  # 5 additional points for no broken/nofollow links

    # Duplicate content (weight: 10%)
    # This could be more complex, but as a placeholder, we assume no duplicates if there is any meaningful content
    word_count_info = seo_report["result"]["word_count"]
    if word_count_info["total"] > 100:  # Assuming meaningful content starts at 100 words
        score += 10  # 10 points for avoiding duplicate/meaningless content

    # On-page SEO factors (weight: 25%)
    keyword_analysis_info = seo_report.get("keyword_analysis", {})
    focus_keyword_found = keyword_analysis_info.get('Focus Keywords Found', 0)
    keyword_density = keyword_analysis_info.get('Keyword Density (%)', 0)
    headings_summary = seo_report["result"]["page_headings_summary"]
    
    if focus_keyword_found > 0:
        score += 10  # 10 points for using focus keywords
    if keyword_density >= 1 and keyword_density <= 3:  # 1-3% keyword density is ideal
        score += 5  # 5 points for good keyword density
    if sum(headings_summary[f'H{i} count'] for i in range(1, 7)) > 0:
        score += 10  # 10 points for using headings correctly

    # User metrics (weight: 20%)
     # User metrics
    if bounce_rate < 50:
        score += 15  # Good bounce rate
    if time_on_page > 30:
        score += 10  # Good time on page
    if pages_per_session > 2:
        score += 10  # Good pages per session

    # Image optimization and loading speed (weight: 10%)
    images_summary = seo_report["result"]["images_analysis"]["summary"]
    if images_summary["total"] > 0 and images_summary["no_alt_tag"] == 0:
        score += 5  # 5 points for optimized images with alt text
    # Assuming fast load time if response time < 2 seconds (a placeholder without load time data)
    if seo_report["result"]["http"]["responseTime"] < 2:
        score += 5  # 5 points for fast image retrieval

    # Ensure the score is capped at 100
    score = min(score, max_score)
    return score

# Function to create a circular gauge chart
def display_seo_score_circle(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        title = {'text': "SEO Score"},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "orange"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': 'red'},
                {'range': [50, 75], 'color': 'yellow'},
                {'range': [75, 100], 'color': 'green'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))

    fig.update_layout(height=350, width=350)
    st.plotly_chart(fig)


# SEO Analyzer Function
def seo_analyzer(url, focus_keyword):
    result = {
        "success": False,
        "message": "",
        "result": {}
    }

    try:
        # Make a request to the URL
        response = requests.get(url)
        status_code = response.status_code
        headers = response.headers
        content_size = len(response.content)

        # HTTP details
        result["result"]["http"] = {
            "status": status_code,
            "using_https": url.startswith("https"),
            "contentSize": {
                "bytes": content_size,
                "kb": round(content_size / 1024, 2)
            },
            "headers": dict(headers),
            "redirections": response.history != [],
            "responseTime": response.elapsed.total_seconds()
        }

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        # text = soup.get_text(separator=' ')

        # Extract text for keyword analysis
        page_text = soup.get_text()

        # Title
        title = soup.title.string if soup.title else "Not found"
        title_length = len(title)
        title_words = len(title.split())
        title_char_per_word = title_length / title_words if title_words > 0 else 0

        result["result"]["title"] = {
            "found": "Found" if soup.title else "Not Found",
            "data": title,
            "length": title_length,
            "words": title_words,
            "charPerWord": round(title_char_per_word, 2),
            "tag number": 1 if soup.title else 0
        }

        # Meta description
        meta_description = soup.find("meta", {"name": "description"})
        meta_desc_content = meta_description["content"] if meta_description else "Not found"
        meta_desc_length = len(meta_desc_content)
        meta_desc_words = len(meta_desc_content.split())
        meta_desc_char_per_word = meta_desc_length / meta_desc_words if meta_desc_words > 0 else 0

        result["result"]["meta_description"] = {
            "found": "Found" if meta_description else "Not Found",
            "data": meta_desc_content,
            "length": meta_desc_length,
            "words": meta_desc_words,
            "charPerWord": round(meta_desc_char_per_word, 2),
            "number": 1 if meta_description else 0
        }

         # Metadata info
        charset = soup.meta.get('charset') if soup.meta else 'Unknown'
        canonical = soup.find("link", {"rel": "canonical"})
        favicon = soup.find("link", {"rel": "icon"})
        viewport = soup.find("meta", {"name": "viewport"})
        keywords = soup.find("meta", {"name": "keywords"})
        robots = soup.find("meta", {"name": "robots"})

        result["result"]["metadata_info"] = {
            "charset": charset,
            "canonical": canonical['href'] if canonical else None,
            "favicon": favicon['href'] if favicon else None,
            "viewport": viewport['content'] if viewport else None,
            "keywords": keywords['content'] if keywords else None,
            "robots": robots['content'] if robots else None,
            "contentType": "website",
            "site_name": None,
            "site_image": None,
            "hreflangs": []
        }

        # Page Headings Summary
        headings = {f'H{i}': [] for i in range(1, 7)}
        for i in range(1, 7):
            heading_tags = soup.find_all(f'h{i}')
            for tag in heading_tags:
                headings[f'H{i}'].append(tag.text.strip())

        result["result"]["page_headings_summary"] = {f'H{i} count': len(headings[f'H{i}']) for i in range(1, 7)}
        result["result"]["page_headings_summary"].update({f'H{i} Content': headings[f'H{i}'] for i in range(1, 7)})

        # Word Count
        # text = soup.get_text()
        words = page_text.split()
        total_word_count = len(words)
        
        result["result"]["word_count"] = {
            "total": total_word_count,
            "corrected_word_count": total_word_count,
            "anchor_text_words": len([link.text.split() for link in soup.find_all('a')]),
            "anchor_percentage": round((len([link.text.split() for link in soup.find_all('a')]) / total_word_count) * 100, 2)
        }

       # Links Summary
        links = soup.find_all('a')
        total_links = len(links)
        external_links = [link['href'] for link in links if link.has_attr('href') and link['href'].startswith('http')]
        internal_links = [link['href'] for link in links if link.has_attr('href') and link['href'].startswith('/')]

        result["result"]["links_summary"] = {
            "total_links": total_links,
            "external_links": len(external_links),
            "internal_links": len(internal_links),
            "nofollow_count": len([link for link in links if 'nofollow' in link.get('rel', [])]),
            "links": [{"href": link['href']} for link in links if link.has_attr('href')]
        }

        # Images Analysis
        images = soup.find_all('img')
        img_data = []
        no_alt = 0
        for img in images:
            alt_text = img.get('alt', '')
            if not alt_text:
                no_alt += 1
            img_data.append({
                "src": img.get('src', ''),
                "alt": alt_text
            })

        result["result"]["images_analysis"] = {
            "summary": {
                "total": len(images),
                "no_src_tag": len([img for img in images if not img.get('src')]),
                "no_alt_tag": no_alt
            },
            "data": img_data
        }

        # If successful
        result["success"] = True
        result["message"] = "Report Generated Successfully"
        result["result"]["page_text"] = page_text  # Store the page text for keyword analysis


    except Exception as e:
        result["message"] = f"Error: {str(e)}"

    return result

# Function to calculate keyword analysis
def keyword_analysis(page_text, keyword):
    keyword = keyword.lower()
    words = page_text.split()

    keyword_count = words.count(keyword)
    keyword_density = (keyword_count / len(words)) * 100 if words else 0
    keyword_positions = [i + 1 for i, word in enumerate(words) if word == keyword]
    keyword_length = len(keyword)
    keyword_chars_per_word = keyword_length / len(keyword.split()) if len(keyword.split()) > 0 else 0

    # Determine the keyword type
    keyword_type = "Short Tail" if len(keyword.split()) == 1 else "Long Tail"

    return {
        'Focus Keyword': keyword,
        'Focus Keywords Found': keyword_count,
        'Focus Keywords Position': keyword_positions,
        'Keywords Character': keyword_length,
        'Keywords Character Per Word': keyword_chars_per_word,
        'Keyword Density (%)': keyword_density,
        'Keyword Frequency': keyword_count / len(set(words)) if words else 0,
        'Keyword Type': keyword_type
    }


# Streamlit UI
def main():
    st.title("SEO Analyzer")
    st.markdown("""
    This tool analyzes the SEO aspects of a webpage. Enter the URL, focus keyword and some necessary parameters below.
    """)

    # Input for URL and Focus Keyword
    url_input = st.text_input("Enter the URL:", "")
    focus_keyword_input = st.text_input("Enter the focus keyword:", "")
    bounce_rate_input = st.number_input("Enter Bounce Rate (%):", min_value=0.0, max_value=100.0, value=50.0)
    time_on_page_input = st.number_input("Enter Time on Page (seconds):", min_value=0.0, value=30.0)
    pages_per_session_input = st.number_input("Enter Average Pages per Session:", min_value=1, value=2)

    # Button to trigger analysis
    if st.button("Analyze"):
        with st.spinner("Analyzing..."):
            # Call the SEO analyzer
            seo_report = seo_analyzer(url_input, focus_keyword_input)

        # Display result
        if seo_report["success"]:
            st.success(seo_report["message"])
            st.header("SEO Analysis Report")

            # Calculate and display SEO Score
            seo_score = calculate_seo_score(seo_report, bounce_rate_input, time_on_page_input, pages_per_session_input)
            st.subheader("SEO Score")
            display_seo_score_circle(seo_score)

            # Display HTTP Details
            st.subheader("HTTP Details")
            http_info = seo_report["result"]["http"]
            st.write(f"**Status Code:** {http_info['status']}")
            st.write(f"**Using HTTPS:** {http_info['using_https']}")
            st.write(f"**Content Size:** {http_info['contentSize']['kb']} KB")
            st.write(f"**Response Time:** {http_info['responseTime']} seconds")

            # Display Title Information
            st.subheader("Title Information")
            title_info = seo_report["result"]["title"]
            st.write(f"**Title Found:** {title_info['found']}")
            st.write(f"**Title:** {title_info['data']}")
            st.write(f"**Length:** {title_info['length']} characters")
            st.write(f"**Words:** {title_info['words']}")
            st.write(f"**Characters per Word:** {title_info['charPerWord']}")

            # Display Meta Description Information
            st.subheader("Meta Description")
            meta_info = seo_report["result"]["meta_description"]
            st.write(f"**Meta Description Found:** {meta_info['found']}")
            st.write(f"**Description:** {meta_info['data']}")
            st.write(f"**Length:** {meta_info['length']} characters")
            st.write(f"**Words:** {meta_info['words']}")
            st.write(f"**Characters per Word:** {meta_info['charPerWord']}")

            # Display Metadata Information
            st.subheader("Metadata Information")
            metadata_info = seo_report["result"]["metadata_info"]
            st.write(f"**Charset:** {metadata_info['charset']}")
            st.write(f"**Canonical:** {metadata_info['canonical']}")
            st.write(f"**Favicon:** {metadata_info['favicon']}")
            st.write(f"**Viewport:** {metadata_info['viewport']}")
            st.write(f"**Keywords:** {metadata_info['keywords']}")
            st.write(f"**Robots:** {metadata_info['robots']}")

            # Display Keyword Analysis
            st.subheader("Keyword Analysis")
            if focus_keyword_input:
                # Use the page text for keyword analysis
                keyword_results = keyword_analysis(seo_report["result"]["page_text"], focus_keyword_input)

                for key, value in keyword_results.items():
                    st.write(f"**{key}:** {value}")

            else:
                st.warning("Please enter a focus keyword to perform keyword analysis.")

            # Display Page Headings Summary
            st.subheader("Headings Summary")
            headings_summary = seo_report["result"]["page_headings_summary"]
            for i in range(1, 7):
                st.write(f"**H{i} Count:** {headings_summary[f'H{i} count']}")
                with st.expander(f"H{i} Content"):
                    st.write(", ".join(headings_summary[f'H{i} Content']))

            # Display Word Count
            st.subheader("Word Count")
            word_count_info = seo_report["result"]["word_count"]
            st.write(f"**Total Words:** {word_count_info['total']}")
            st.write(f"**Corrected Word Count:** {word_count_info['corrected_word_count']}")
            st.write(f"**Anchor Text Words:** {word_count_info['anchor_text_words']}")
            st.write(f"**Anchor Percentage:** {word_count_info['anchor_percentage']}%")

            # Display Links Summary
            st.subheader("Links Summary")
            links_summary = seo_report["result"]["links_summary"]
            st.write(f"**Total Links:** {links_summary['total_links']}")
            st.write(f"**External Links:** {links_summary['external_links']}")
            st.write(f"**Internal Links:** {links_summary['internal_links']}")
            st.write(f"**Nofollow Count:** {links_summary['nofollow_count']}")

            # Links Dropdown
            with st.expander("View Links", expanded=True):
                for link in links_summary["links"]:
                    st.write(link["href"])

            # Display Images Analysis
            st.subheader("Images Analysis")
            img_summary = seo_report["result"]["images_analysis"]["summary"]
            st.write(f"**Total Images:** {img_summary['total']}")
            st.write(f"**Images with No src tag:** {img_summary['no_src_tag']}")
            st.write(f"**Images with No alt tag:** {img_summary['no_alt_tag']}")

            # Images Dropdown
            with st.expander("View Images", expanded=True):
                for img in seo_report["result"]["images_analysis"]["data"]:
                    st.write(f"Image Source: {img['src']} | Alt Text: {img['alt']}")

        else:
            st.error(seo_report["message"])

if __name__ == "__main__":
    main()

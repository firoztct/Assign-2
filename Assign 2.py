import openai
import os
import requests
import base64
from dotenv import load_dotenv
load_dotenv()

openai_api = os.getenv("api_key")
wp_user = os.getenv("user_name")
wp_pw = os.getenv("wp_pw")
url = os.getenv("url")
api_endpoint = f"{url}/wp-json/wp/v2/posts"
wp_credential = f'{wp_user}:{wp_pw}'
wp_token = base64.b64encode(wp_credential.encode())
wp_headers = {'Authorization': f'Basic {wp_token.decode("utf-8")}'}


def text_render(prompt):

  """
  This Function will Generate WP Post Intro & Outline Paragraph
  :param prompt: Input Keyword
  :return: This will Return Intro & Outline Paragraph based on Providing Keyword.
  """
  openai.api_key = openai_api
  response = openai.Completion.create(
    model="text-davinci-002",
    prompt=prompt,
    temperature=0.7,
    max_tokens=500,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
  )
  return response["choices"][0].get("text").strip()


def text_formatting(text):

  """
  This function will convert Text to HTML in Gutenberg Formate.
  """
  text = text.replace('.', '.---').split('---')
  retun_text1 = '<!-- wp:paragraph --><p>' + ''.join(text[0:3]) + '</p><!-- /wp:paragraph -->'
  retun_text2 = '<!-- wp:paragraph --><p>' + ''.join(text[3:6]) + '</p><!-- /wp:paragraph -->'
  retun_text3 = '<!-- wp:paragraph --><p>' + ''.join(text[6:9]) + '</p><!-- /wp:paragraph -->'
  retun_text4 = '<!-- wp:paragraph --><p>' + ''.join(text[9:12]) + '</p><!-- /wp:paragraph -->'
  retun_text5 = '<!-- wp:paragraph --><p>' + ''.join(text[12:]) + '</p><!-- /wp:paragraph -->'

  return retun_text1 + retun_text2 + retun_text3 + retun_text4 + retun_text5


with open("keywords.txt", "r+") as file:
  file = file.readlines()
  for keyword in file:
    outline = text_render(f'Write a killer blog outline for the following request from a customer.\n\nREQUEST:{keyword}\n\nBrainstorm a list of sections for this blog post. The outline should meet the customer\'s request and each section should be highly descriptive.\n\nSECTIONS:\n\n1.')
    improve_outlines = text_render(f'I brainstormed the following list of sections of a blog based on the customer\'s request. I need to brainstorm to see if there are any improvements I can make to this outline.\n\nREQUEST:{keyword}\n\nOUTLINE:\n{outline}\n\nBrainstorm some possible improvements:\n\n1.')
    outline_list = improve_outlines.splitlines()
    final_outlines = []
    for headings in outline_list:
      if " " in headings and "Introduction" not in headings and "Conclusion" not in headings:
        final_outlines.append(headings.replace("1.", "").replace("2.", "").replace("3.", "").replace("4.", "").replace("5.", "").replace("6.", "").replace("7.", "").replace("8.", "").replace("9.", "").replace("10.", "").strip())

    post_intro = '<!-- wp:paragraph --><p>'+text_render(f'Write high blog introduction Between 120 to 180 words, Topic:{keyword}:')+'</p><!-- /wp:paragraph -->'

    post_body = post_intro
    for key in final_outlines:
      heading_two = f'<!-- wp:heading --><h2>{key}</h2><!-- /wp:heading -->' + text_formatting(text_render(
        f'"""\nBlog Section Title: {key}, Main Keyword: {keyword}\n"""\nWrite this blog section into a details professional para, witty and clever explanation:'))
      post_body += heading_two

    conclusion = '<!-- wp:heading --><h2>Conclusion</h2><!-- /wp:heading -->'+'<!-- wp:paragraph --><p>'+text_render(f'Write a Conclusion max 150 words, Topic:{keyword}:')+'</p><!-- /wp:paragraph -->'
    post_body += conclusion

    # WP Posting
    wp_title = f"{keyword} Buying Guide 2022"
    content = post_body
    slug = keyword.replace(' ', '-').lower()

    post = {'title': wp_title,
            'slug': slug,
            'status': 'draft',
            'content': content,
            'format': 'standard',
            }
    wp_posting = requests.post(api_endpoint, headers=wp_headers, data=post)

    if wp_posting.status_code == 201:
      print(f"{url}/{slug} >>> Post Successful")
    else:
      print("Error")
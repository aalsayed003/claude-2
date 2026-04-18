"""Render a sample report with mock competitor data.

This bypasses Instagram and Claude so we can preview the email layout.
NOT used in production — only for local preview when scraping/Claude is unavailable.
"""

from pathlib import Path

from src.scraper import CompetitorData, Post

MOCK = [
    CompetitorData(
        name="Ibn Al Nafees",
        username="ibnalnafees",
        followers=42_300,
        posts=[
            Post(
                shortcode="C1abc",
                url="https://www.instagram.com/p/C1abc/",
                caption="We are proud to announce our new Robotic Surgery Unit, equipped with the latest da Vinci Xi system. First procedures begin next month.",
                posted_at="2026-04-15T09:00:00+00:00",
                likes=1_842,
                comments=127,
                is_video=True,
                video_view_count=18_400,
                hashtags=["robotics", "healthcare", "bahrain", "innovation"],
            ),
            Post(
                shortcode="C1def",
                url="https://www.instagram.com/p/C1def/",
                caption="Ramadan Kareem from the Ibn Al Nafees family. Our 24/7 emergency services remain fully staffed throughout the holy month.",
                posted_at="2026-04-13T18:30:00+00:00",
                likes=612,
                comments=24,
                is_video=False,
                video_view_count=None,
                hashtags=["ramadan", "ramadankareem"],
            ),
        ],
    ),
    CompetitorData(
        name="Kindi Hospital",
        username="alkindihospital",
        followers=28_900,
        posts=[
            Post(
                shortcode="C2xyz",
                url="https://www.instagram.com/p/C2xyz/",
                caption="Free diabetes screening campaign continues this week. Walk-in clinic open Sat-Thu, 9am-5pm. Partnered with the Bahrain Diabetes Society.",
                posted_at="2026-04-16T10:00:00+00:00",
                likes=945,
                comments=88,
                is_video=False,
                video_view_count=None,
                hashtags=["diabetes", "screening", "bahrain"],
            ),
            Post(
                shortcode="C2pqr",
                url="https://www.instagram.com/p/C2pqr/",
                caption="Meet Dr. Layla Al-Mannai, our new Head of Pediatrics. Twenty years of experience at leading London hospitals.",
                posted_at="2026-04-14T11:15:00+00:00",
                likes=1_103,
                comments=56,
                is_video=False,
                video_view_count=None,
                hashtags=["pediatrics", "newdoctor"],
            ),
        ],
    ),
    CompetitorData(
        name="American Mission Hospital",
        username="american_mission_hospital",
        followers=51_700,
        posts=[
            Post(
                shortcode="C3aaa",
                url="https://www.instagram.com/p/C3aaa/",
                caption="Launching our IVF & Fertility Center next month. Bahrain's first dedicated end-to-end fertility program with on-site embryology lab.",
                posted_at="2026-04-17T08:00:00+00:00",
                likes=2_341,
                comments=192,
                is_video=True,
                video_view_count=24_900,
                hashtags=["ivf", "fertility", "newcenter", "bahrain"],
            ),
        ],
    ),
    CompetitorData(
        name="Royal Bahrain Hospital",
        username="royalbahrainhospital",
        followers=63_200,
        posts=[
            Post(
                shortcode="C4mmm",
                url="https://www.instagram.com/p/C4mmm/",
                caption="Patient story: Mohammed, 58, walked out of cardiac rehab today after a successful triple bypass. Watch his journey.",
                posted_at="2026-04-15T14:00:00+00:00",
                likes=3_205,
                comments=241,
                is_video=True,
                video_view_count=41_200,
                hashtags=["cardiac", "patientstory", "recovery"],
            ),
            Post(
                shortcode="C4nnn",
                url="https://www.instagram.com/p/C4nnn/",
                caption="New WhatsApp booking line is now live: +973-1234-5678. Book outpatient appointments directly without calling.",
                posted_at="2026-04-12T09:30:00+00:00",
                likes=487,
                comments=42,
                is_video=False,
                video_view_count=None,
                hashtags=["booking", "whatsapp"],
            ),
        ],
    ),
]

SAMPLE_HTML = """
<h2>Executive Summary</h2>
<p>Three of the four competitors launched <strong>new clinical capabilities</strong> this week:
Ibn Al Nafees rolled out robotic surgery, AMH announced a fertility center, and Kindi added a
diabetes screening campaign. Royal Bahrain led on engagement with a patient-story video
(3,205 likes / 241 comments). Video and patient-narrative content significantly outperformed
service announcements.</p>

<h2>Top Posts by Engagement</h2>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; width: 100%;">
  <tr style="background:#f0f0f0;">
    <th align="left">Competitor</th><th>Likes</th><th>Comments</th><th>Total</th><th>Post</th>
  </tr>
  <tr><td>Royal Bahrain</td><td>3,205</td><td>241</td><td>3,446</td><td><a href="https://www.instagram.com/p/C4mmm/">Cardiac patient story</a></td></tr>
  <tr><td>American Mission Hospital</td><td>2,341</td><td>192</td><td>2,533</td><td><a href="https://www.instagram.com/p/C3aaa/">IVF center launch</a></td></tr>
  <tr><td>Ibn Al Nafees</td><td>1,842</td><td>127</td><td>1,969</td><td><a href="https://www.instagram.com/p/C1abc/">Robotic surgery announcement</a></td></tr>
  <tr><td>Kindi Hospital</td><td>1,103</td><td>56</td><td>1,159</td><td><a href="https://www.instagram.com/p/C2pqr/">New head of pediatrics</a></td></tr>
</table>

<h2>What Competitors Are Offering That's New</h2>
<p><strong>Ibn Al Nafees</strong></p>
<ul>
  <li>New <strong>Robotic Surgery Unit</strong> with da Vinci Xi system, first procedures next month</li>
</ul>
<p><strong>Kindi Hospital</strong></p>
<ul>
  <li>Free <strong>diabetes screening campaign</strong> this week, partnered with Bahrain Diabetes Society</li>
  <li>Hired <strong>Dr. Layla Al-Mannai</strong> (London-trained) as Head of Pediatrics</li>
</ul>
<p><strong>American Mission Hospital</strong></p>
<ul>
  <li>Launching <strong>IVF &amp; Fertility Center</strong> next month — claims Bahrain's first end-to-end program with on-site embryology lab</li>
</ul>
<p><strong>Royal Bahrain Hospital</strong></p>
<ul>
  <li>New <strong>WhatsApp booking line</strong> for outpatient appointments — direct booking without phone call</li>
</ul>

<h2>Content Themes Driving Engagement</h2>
<ul>
  <li><strong>Video posts dominated.</strong> All three top-engaging posts this week were videos. Average engagement on videos: ~2,460 interactions vs ~660 for static images.</li>
  <li><strong>Patient stories outperform service announcements 1.7x.</strong> Royal Bahrain's cardiac recovery story beat AMH's IVF launch despite AMH having a bigger announcement.</li>
  <li><strong>"New service" posts get strong saves and comments</strong> — Ibn Al Nafees and AMH both saw heavy comment volume on their new-capability launches.</li>
  <li>Hashtag pattern: competitors use 2-4 tags max, mixing service tags (#robotics, #ivf) with location (#bahrain).</li>
</ul>

<h2>Recommendations for Al Salam</h2>
<ol>
  <li><strong>Lead with patient-story video this week.</strong> Royal Bahrain's format (named patient + journey + walk-out moment) is the highest-engagement format in the set. Pick one recovery story from the past 30 days and produce a 60-90 second vertical video.</li>
  <li><strong>Pre-empt AMH's IVF launch with a counter-positioning post</strong> within 7 days. If Al Salam offers fertility services, reframe what we already do; if not, communicate a complementary specialty (e.g. women's health, neonatal) to capture the same audience search interest.</li>
  <li><strong>Launch a free screening campaign</strong> for one condition where we're strong (Kindi's diabetes campaign generated 945 likes / 88 comments at lower follower count — high efficiency). Pair with a recognized partner for credibility.</li>
  <li><strong>Add a WhatsApp booking number to bio + announcement post.</strong> Royal Bahrain's bookings post got modest likes but the utility-value drives DM and saves; this is a low-cost feature with retention payoff.</li>
  <li><strong>Audit our video-to-image post ratio.</strong> If we're below 50% video, raise it. Allocate next month's content budget toward 2 produced videos per week.</li>
</ol>

<hr>
<p style="color:#888;font-size:12px;">Generated by the Al Salam Competitor Intelligence agent. Reply to this email to flag corrections.</p>
"""


def main():
    out = Path("report.html")
    out.write_text(SAMPLE_HTML)
    print(f"Wrote {out.absolute()}")
    print("\nMock data summary:")
    for c in MOCK:
        print(f"  {c.name}: {len(c.posts)} posts, {c.followers:,} followers")


if __name__ == "__main__":
    main()

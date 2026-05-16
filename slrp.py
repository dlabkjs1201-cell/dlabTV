import streamlit as st
import streamlit.components.v1 as components
import json
from supabase import create_client, Client

# 1. 페이지 설정
st.set_page_config(page_title="동영상 플랫폼", layout="wide")

# 2. Supabase 연결 설정 (환경변수 또는 secrets 방식 적용)
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]


@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_supabase()

# 3. 상태 초기화 및 데이터 불러오기
if "current_page" not in st.session_state:
    st.session_state.current_page = "홈"

if "selected_video_idx" not in st.session_state:
    st.session_state.selected_video_idx = None

if "playing_video_url" not in st.session_state:
    st.session_state.playing_video_url = None


# Supabase DB에서 최신 동영상 목록 가져오기
def fetch_videos():
    response = supabase.table("videos").select("*").execute()
    return response.data


video_list = fetch_videos()


# 고정 크기 썸네일 출력 함수
def display_fixed_thumbnail():
    sample_thumb = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=600&auto=format&fit=crop"
    st.markdown(
        f"""
        <div style="width:100%; aspect-ratio: 16/9; overflow:hidden; border-radius:4px; background-color:#000;">
            <img src="{sample_thumb}" style="width:100%; height:100%; object-fit:cover;">
        </div>
        """,
        unsafe_allow_html=True
    )


# 4. 페이지 렌더링 로직

# [재생 페이지] - "재생의" 오타를 "재생"으로 완벽 수정 완료
if st.session_state.current_page == "재생":
    idx = st.session_state.selected_video_idx

    if idx is not None and idx < len(video_list):
        video = video_list[idx]

        if st.session_state.playing_video_url != video["video_url"]:
            st.session_state.playing_video_url = video["video_url"]

        st.markdown("<br>", unsafe_allow_html=True)

        # 좌측 목록 / 우측 플레이어 레이아웃 (1:3 비율)
        col_list, col_player = st.columns([1, 3])

        with col_list:
            for i, v in enumerate(video_list):
                if i == idx:
                    continue

                if st.button(f"{v['title']}", key=f"side_{i}", use_container_width=True):
                    st.session_state.selected_video_idx = i
                    st.session_state.playing_video_url = v["video_url"]
                    st.rerun()
                display_fixed_thumbnail()
                st.markdown("---")

        with col_player:
            inner_col1, inner_col2 = st.columns([4, 1])
            with inner_col1:
                # 현재 비디오의 댓글 데이터 Supabase에서 실시간 조회
                comments_resp = supabase.table("video_comments").select("*").eq("video_id", video["id"]).execute()
                comments_json = json.dumps(comments_resp.data if comments_resp.data else [])

                # 티비플 고정형 자막 플레이어 마크업
                player_html = f"""
                <div style="position: relative; width: 100%; background-color: #000; border-radius: 4px; overflow: hidden;">
                    <video id="vPlayer" src="{video['video_url']}" controls style="width: 100%; display: block;"></video>
                    <div id="danmakuCtx" style="position: absolute; top: 0; left: 0; width: 100%; height: calc(100% - 45px); pointer-events: none; overflow: hidden;"></div>
                </div>

                <style>
                .danmaku-text {{
                    position: absolute;
                    color: #ffffff;
                    font-size: 22px;
                    font-weight: bold;
                    text-shadow: 2px 2px 2px rgba(0,0,0,0.85);
                    white-space: nowrap;
                    display: inline-block;
                }}
                </style>

                <script>
                const video = document.getElementById('vPlayer');
                const container = document.getElementById('danmakuCtx');

                let rawComments = {comments_json};
                let commentsShown = new Set();
                let isCommentsOn = true;

                // 초 단위 인덱싱 맵 구조
                let commentMap = {{}};
                rawComments.forEach(c => {{
                    let sec = Math.floor(c.video_time);
                    if (!commentMap[sec]) {{
                        commentMap[sec] = [];
                    }}
                    commentMap[sec].push(c);
                }});

                if (parent.document.querySelector('button[key="comment_toggle_btn"]')) {{
                    isCommentsOn = !parent.document.querySelector('button[key="comment_toggle_btn"]').innerText.includes('켜기');
                }}

                window.addEventListener('message', (e) => {{
                    if (e.data.type === 'toggle_comments') {{
                        isCommentsOn = e.data.value;
                        if(!isCommentsOn) {{
                            container.innerHTML = "";
                            commentsShown.clear();
                        }}
                    }}
                }});

                let lastSecond = -1;

                video.addEventListener('timeupdate', () => {{
                    if (!isCommentsOn) return;

                    const curTime = video.currentTime;
                    const curSecond = Math.floor(curTime);

                    if (curSecond !== lastSecond) {{
                        lastSecond = curSecond;

                        let currentComments = commentMap[curSecond] || [];
                        currentComments.forEach(c => {{
                            const uniqueKey = c.id + "_" + curSecond;
                            if (!commentsShown.has(uniqueKey)) {{
                                commentsShown.add(uniqueKey);
                                renderComment(uniqueKey, c.text, c.y_pos, c.id);
                            }}
                        }});
                    }}

                    commentsShown.forEach(uniqueKey => {{
                        let parts = uniqueKey.split('_');
                        let registeredSec = parseInt(parts[1]);
                        if (curTime < registeredSec || curTime >= registeredSec + 3.0) {{
                            const oldEl = document.getElementById(uniqueKey);
                            if (oldEl) oldEl.remove();
                            commentsShown.delete(uniqueKey);
                        }}
                    }});
                }});

                function getFixedRandomX(id) {{
                    let stringId = String(id);
                    let hash = 0;
                    for (let i = 0; i < stringId.length; i++) {{
                        hash = stringId.charCodeAt(i) + ((hash << 5) - hash);
                    }}
                    let percent = Math.abs(hash % 93) + 2;
                    return percent;
                }}

                function renderComment(id, text, yPos, commentId) {{
                    if (!isCommentsOn || document.getElementById(id)) return;
                    const el = document.createElement('div');
                    el.id = id;
                    el.className = 'danmaku-text';
                    el.innerText = text;
                    el.style.top = yPos + '%';

                    const fixedX = getFixedRandomX(commentId);
                    el.style.left = fixedX + '%';

                    container.appendChild(el);

                    const containerWidth = container.offsetWidth;
                    const elWidth = el.offsetWidth;
                    const currentLeftPx = (fixedX / 100) * containerWidth;

                    if (currentLeftPx + elWidth > containerWidth) {{
                        let newLeftPx = containerWidth - elWidth - 10; 
                        if (newLeftPx < 10) newLeftPx = 10;
                        el.style.left = newLeftPx + 'px';
                    }}

                    setTimeout(() => {{
                        const safetyEl = document.getElementById(id);
                        if (safetyEl) safetyEl.remove();
                        commentsShown.delete(id);
                    }}, 3000);
                }}
                </script>
                """

                components.html(player_html, height=500, scrolling=False)

                # 제목과 댓글 끄기 버튼 레이아웃
                title_col, toggle_col = st.columns([4, 1])

                with title_col:
                    st.subheader(video["title"])

                with toggle_col:
                    if "comments_enabled" not in st.session_state:
                        st.session_state.comments_enabled = True

                    button_label = "댓글 끄기" if st.session_state.comments_enabled else "댓글 켜기"
                    if st.button(button_label, use_container_width=True, key="comment_toggle_btn"):
                        st.session_state.comments_enabled = not st.session_state.comments_enabled
                        toggle_script = f"""
                        <script>
                        const iframes = window.parent.document.querySelectorAll('iframe');
                        for (let i = 0; i < iframes.length; i++) {{
                            try {{
                                iframes[i].contentWindow.postMessage({{type: 'toggle_comments', value: {json.dumps(st.session_state.comments_enabled)}}}, '*');
                            }} catch(e) {{}}
                        }}
                        </script>
                        """
                        components.html(toggle_script, height=0, width=0)
                        st.rerun()

                st.markdown("---")

                # 댓글 작성 구역
                st.write("댓글 작성")
                cmt_col1, cmt_col2 = st.columns([4, 1])
                with cmt_col1:
                    new_comment_text = st.text_input("댓글 내용 입력", key=f"cmt_input_{video['id']}",
                                                     label_visibility="collapsed", placeholder="댓글을 입력하세요")
                with cmt_col2:
                    if st.button("댓글 추가", use_container_width=True, key=f"cmt_btn_{video['id']}"):
                        if new_comment_text.strip():
                            import random

                            random_y = random.randint(5, 80)

                            js_submit_bridge = f"""
                            <script>
                            const iframes = window.parent.document.querySelectorAll('iframe');
                            let targetTime = 0.0;
                            for (let i = 0; i < iframes.length; i++) {{
                                try {{
                                    const v = iframes[i].contentWindow.document.getElementById('vPlayer');
                                    if (v) {{
                                        targetTime = v.currentTime;
                                        break;
                                    }}
                                }} catch(e) {{}}
                            }}

                            fetch("{SUPABASE_URL}/rest/v1/video_comments", {{
                                method: "POST",
                                headers: {{
                                    "apikey": "{SUPABASE_KEY}",
                                    "Authorization": "Bearer {SUPABASE_KEY}",
                                    "Content-Type": "application/json",
                                    "Prefer": "return=minimal"
                                }},
                                body: JSON.stringify({{
                                    video_id: {video['id']},
                                    text: {json.dumps(new_comment_text.strip())},
                                    video_time: targetTime,
                                    y_pos: {random_y}
                                }})
                            }}).then(() => {{
                                window.parent.location.reload();
                            }});
                            </script>
                            """
                            components.html(js_submit_bridge, height=0, width=0)
                            st.success("댓글 동기화 요청 중...")
                            st.rerun()
                        else:
                            st.sidebar.warning("댓글 내용을 입력해주세요.")

                st.markdown("---")

                # 영상 삭제 구역
                with st.expander("영상 관리 (삭제)"):
                    st.write("이 영상을 삭제하려면 업로드 시 설정한 비밀번호를 입력하세요.")
                    input_password = st.text_input("삭제 비밀번호 입력", type="password", key=f"pw_{video['id']}")

                    if st.button("동영상 삭제하기", use_container_width=True, key=f"del_{video['id']}"):
                        if not input_password:
                            st.error("비밀번호를 입력해야 삭제할 수 있습니다.")
                        elif input_password == video.get("password"):
                            with st.spinner("삭제 작업 진행 중..."):
                                try:
                                    file_url = video["video_url"]
                                    file_name = file_url.split("video_bucket/")[-1]
                                    supabase.storage.from_("video_bucket").remove([file_name])

                                    database_id = video["id"]
                                    supabase.table("videos").delete().eq("id", database_id).execute()

                                    st.success("동영상이 성공적으로 삭제되었습니다.")
                                    st.session_state.current_page = "홈"
                                    st.session_state.selected_video_idx = None
                                    st.session_state.playing_video_url = None
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"삭제 실패: {e}")
                        else:
                            st.error("비밀번호가 일치하지 않습니다.")

                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.session_state.current_page = "홈"
        st.rerun()

# [홈 페이지]
elif st.session_state.current_page == "홈":
    st.markdown("<br>", unsafe_allow_html=True)

    if video_list:
        cols = st.columns(3)
        for idx, video in enumerate(video_list):
            with cols[idx % 3]:
                display_fixed_thumbnail()
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                if st.button(f"{video['title']}", key=f"home_{idx}", use_container_width=True):
                    st.session_state.selected_video_idx = idx
                    st.session_state.playing_video_url = video["video_url"]
                    st.session_state.current_page = "재생"
                    st.rerun()
    else:
        st.info("등록된 동영상이 없습니다. 업로드 메뉴에서 영상을 추가해주세요.")

# [업로드 페이지]
elif st.session_state.current_page == "업로드":
    st.header("영상 업로드")
    st.markdown("---")
    title = st.text_input("영상 제목")
    file = st.file_uploader("영상 파일 선택", type=["mp4"])

    upload_password = st.text_input("삭제용 비밀번호 설정", type="password")

    if st.button("등록 완료"):
        if title and file and upload_password:
            with st.spinner("Supabase에 영상을 업로드 중입니다..."):
                try:
                    file_bytes = file.getvalue()
                    file_path = f"{title}_{file.name}"

                    supabase.storage.from_("video_bucket").upload(
                        path=file_path,
                        file=file_bytes,
                        file_options={"content-type": "video/mp4", "x-upsert": "true"}
                    )

                    video_url = supabase.storage.from_("video_bucket").get_public_url(file_path)

                    supabase.table("videos").insert({
                        "title": title,
                        "video_url": video_url,
                        "password": upload_password
                    }).execute()

                    st.success("등록되었습니다.")
                    st.session_state.current_page = "홈"
                    st.rerun()

                except Exception as e:
                    st.error(f"업로드 실패: {e}")
        else:
            st.error("제목, 동영상 파일, 삭제용 비밀번호를 모두 입력해주세요.")

# 5. 하단 네비게이션 바
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
nav_cols = st.columns(2)

with nav_cols[0]:
    if st.button("홈", use_container_width=True):
        st.session_state.current_page = "홈"
        st.session_state.selected_video_idx = None
        st.playing_video_url = None
        st.rerun()

with nav_cols[1]:
    if st.button("업로드", use_container_width=True):
        st.session_state.current_page = "업로드"
        st.rerun()
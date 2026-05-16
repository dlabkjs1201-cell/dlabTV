import streamlit as st
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
    sample_thumb = "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=500"
    st.markdown(
        f"""
        <div style="width:100%; aspect-ratio: 16/9; overflow:hidden; border-radius:4px; background-color:#000;">
            <img src="{sample_thumb}" style="width:100%; height:100%; object-fit:cover;">
        </div>
        """,
        unsafe_allow_html=True
    )


# 4. 페이지 렌더링 로직

# [재생 페이지]
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
                st.video(st.session_state.playing_video_url)
                st.subheader(video["title"])

                st.markdown("---")
                # 삭제 비밀번호 입력 및 버튼 구역
                st.write("동영상 관리를 위해 삭제하려면 업로드 시 설정한 비밀번호를 입력하세요.")
                input_password = st.text_input("삭제 비밀번호 입력", type="password", key=f"pw_{video['id']}")

                if st.button("동영상 삭제하기", use_container_width=True, key=f"del_{video['id']}"):
                    if not input_password:
                        st.error("비밀번호를 입력해야 삭제할 수 있습니다.")
                    # 입력한 비밀번호와 DB에 저장된 비밀번호 비교
                    elif input_password == video.get("password"):
                        with st.spinner("삭제 작업 진행 중..."):
                            try:
                                # 1. 스토리지에서 파일 삭제
                                file_url = video["video_url"]
                                file_name = file_url.split("video_bucket/")[-1]
                                supabase.storage.from_("video_bucket").remove([file_name])

                                # 2. DB 테이블에서 행 삭제
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
                st.subheader(video["title"])
                if st.button("시청하기", key=f"home_{idx}", use_container_width=True):
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

    # 동영상 등록 시 사용할 비밀번호 입력 필드 추가
    upload_password = st.text_input("삭제용 비밀번호 설정", type="password")

    if st.button("등록 완료"):
        if title and file and upload_password:
            with st.spinner("Supabase에 영상을 업로드 중입니다..."):
                try:
                    file_bytes = file.getvalue()
                    file_path = f"{title}_{file.name}"

                    # 1. Supabase 스토리지에 파일 업로드
                    supabase.storage.from_("video_bucket").upload(
                        path=file_path,
                        file=file_bytes,
                        file_options={"content-type": "video/mp4", "x-upsert": "true"}
                    )

                    video_url = supabase.storage.from_("video_bucket").get_public_url(file_path)

                    # 2. DB 테이블에 제목, URL, 설정한 비밀번호까지 함께 저장
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
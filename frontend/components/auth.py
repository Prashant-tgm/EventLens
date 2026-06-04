"""
Authentication page — Split-screen hero + glassmorphism login card.
"""
import streamlit as st
from utils.api_client import api_client


def show_auth_page():
    # Hero section
    st.markdown("""
    <div class="hero-section slide-up">
        <div class="hero-title">Find Every Photo<br>Instantly</div>
        <div class="hero-subtitle">
            AI-powered face recognition to help your guests find their photos
            in under 2 seconds. Upload, detect, cluster, retrieve.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Centered auth card
    col_spacer_l, col_form, col_spacer_r = st.columns([1, 2, 1])

    with col_form:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)

        tabs = st.tabs(["Sign In", "Create Account"])

        # ── Login Tab ────────────────────────────────────────────────────
        with tabs[0]:
            st.markdown("""
            <p style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 20px;">
                Access your dashboard to manage events, uploads, and team.
            </p>
            """, unsafe_allow_html=True)

            email = st.text_input("Email address", key="login_email",
                                  placeholder="you@studio.com")
            password = st.text_input("Password", type="password", key="login_pwd",
                                     placeholder="••••••••")

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

            if st.button("Sign In →", use_container_width=True, key="btn_login"):
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    with st.spinner("Authenticating..."):
                        success = api_client.login(email, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.email = email
                        try:
                            user_info = api_client.get_me()
                            st.session_state.user_role = user_info.get("role", "photographer")
                            st.session_state.user_id = user_info.get("user_id")
                        except Exception:
                            st.session_state.user_role = "photographer"
                        st.session_state.current_page = "dashboard"
                        st.rerun()
                    else:
                        st.error("Invalid email or password. Please try again.")

            st.markdown("""
            <p style="text-align: center; color: #64748B; font-size: 0.75rem; margin-top: 16px;">
                Forgot your password? Contact your administrator.
            </p>
            """, unsafe_allow_html=True)

        # ── Register Tab ─────────────────────────────────────────────────
        with tabs[1]:
            st.markdown("""
            <p style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 20px;">
                Join as an Event Owner or Team Photographer.
            </p>
            """, unsafe_allow_html=True)

            reg_email = st.text_input("Email address", key="reg_email",
                                      placeholder="you@studio.com")
            reg_password = st.text_input("Create password", type="password",
                                         key="reg_pwd",
                                         placeholder="Minimum 8 characters")

            # Role selector as radio pills
            reg_role = st.radio(
                "I am registering as",
                ["Event Owner", "Photographer"],
                horizontal=True,
                key="reg_role",
            )

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

            if st.button("Create Account →", use_container_width=True, key="btn_register"):
                if not reg_email or not reg_password:
                    st.error("Please fill in all fields.")
                elif len(reg_password) < 8:
                    st.error("Password must be at least 8 characters.")
                else:
                    role_val = "owner" if reg_role == "Event Owner" else "photographer"
                    with st.spinner("Creating your account..."):
                        try:
                            api_client.register(reg_email, reg_password, role_val)
                            st.success("Account created! Switch to Sign In to access your dashboard.")
                        except Exception as e:
                            st.error(f"Registration failed: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

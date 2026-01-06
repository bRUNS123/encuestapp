import axiosInstance from "@/store/axiosInstance";
import { createStore } from "vuex";
import router from "@/router";

export default createStore({
  state: {
    preguntas: [],
    rightBarPreguntas: [],
    userPreguntas: [], // Separate state for user profile questions
    loading: false,
    error: null,
    accessToken: localStorage.getItem("access_token") || "",
    refreshToken: localStorage.getItem("refresh_token") || "",
    user: null,
    compatibilityList: [],
    comments: {},
    profilesList: [],
    friendVotes: [],
    globalStats: null,
  },
  mutations: {
    SET_PREGUNTAS(state, preguntas) {
      console.log('🔄 SET_PREGUNTAS called with', preguntas.length, 'items');
      state.preguntas = preguntas;
    },
    SET_USER_PREGUNTAS(state, preguntas) {
      state.userPreguntas = preguntas;
    },
    REMOVE_USER_VOTE(state, questionId) {
      const updateData = (list) => {
        const question = list.find(q => q.id === questionId);
        if (question) {
          question.current_user_answer = null;
          question.user_has_voted = false;
          question.user_vote_is_public = null;
          question.user_rating = 0;
          question.hidden = true; // Mark as hidden locally
          question.cantidad_votos = Math.max(0, question.cantidad_votos - 1);
        }
      };

      updateData(state.preguntas);
      updateData(state.userPreguntas);
    },
    SET_RIGHTBAR_PREGUNTAS(state, preguntas) {
      state.rightBarPreguntas = preguntas;
    },
    SET_LOADING(state, loading) {
      state.loading = loading;
    },
    SET_ERROR(state, error) {
      state.error = error;
    },
    CLEAR_ERROR(state) {
      state.error = null;
    },
    UPDATE_VOTE(state, updatedPregunta) {
      const index = state.preguntas.findIndex(
        (p) => p.id === updatedPregunta.id
      );
      if (index !== -1) {
        state.preguntas[index] = updatedPregunta;
      }
    },
    SET_ACCESS_TOKEN(state, token) {
      state.accessToken = token;
      localStorage.setItem("access_token", token);
    },
    SET_REFRESH_TOKEN(state, token) {
      state.refreshToken = token;
      localStorage.setItem("refresh_token", token);
    },
    SET_USER(state, user) {
      state.user = user;
      state.user.votesCount = user.votes ? user.votes.length : 0;
    },
    SET_COMPATIBILITY_LIST(state, list) {
      state.compatibilityList = list;
    },
    SET_PROFILES_LIST(state, list) {
      state.profilesList = list;
    },
    UPDATE_PROFILE_STATUS(state, { id, status }) {
      const profile = state.profilesList.find(p => p.id === id);
      if (profile) {
        profile.friendship_status = status;
      }
    },
    SET_FRIEND_VOTES(state, votes) {
      state.friendVotes = votes;
    },
    UPDATE_VOTE(state, updatedQuestion) {
      const index = state.preguntas.findIndex((p) => p.id === updatedQuestion.id);
      if (index !== -1) {
        state.preguntas[index] = updatedQuestion;
      }
    },
    LOGOUT(state) {
      state.accessToken = "";
      state.refreshToken = "";
      state.user = null;
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    },
    SET_COMMENTS(state, { questionId, comments }) {
      state.comments = { ...state.comments, [questionId]: comments };
    },
    ADD_COMMENT(state, comment) {
      const currentComments = state.comments[comment.question] || [];
      state.comments = {
        ...state.comments,
        [comment.question]: [comment, ...currentComments]
      };
    },
    SET_COMPATIBILITY_LIST(state, list) {
      state.compatibilityList = list;
    },
    SET_GLOBAL_STATS(state, stats) {
      state.globalStats = stats;
    },
    UPDATE_QUESTION_RATING(state, { questionId, ratingAverage, ratingCount, userRating }) {
      const question = state.preguntas.find(q => q.id === questionId);
      if (question) {
        question.rating_average = ratingAverage;
        question.rating_count = ratingCount;
        question.user_rating = userRating;
      }
      // Also update rightBarPreguntas if present
      const questionRB = state.rightBarPreguntas.find(q => q.id === questionId);
      if (questionRB) {
        questionRB.rating_average = ratingAverage;
        questionRB.rating_count = ratingCount;
        questionRB.user_rating = userRating;
      }
    },
  },
  actions: {
    async fetchPreguntas({ commit }) {
      commit("SET_LOADING", true);
      commit("SET_ERROR", null);
      let url = "/questions/";
      let allPreguntas = [];
      try {
        while (url) {
          const response = await axiosInstance.get(url);
          const data = response.data;
          if (data && Array.isArray(data.results)) {
            allPreguntas = allPreguntas.concat(data.results);
            url = data.next; // URL de la próxima página
          } else {
            throw new Error("Datos inválidos");
          }
        }
        console.log('✅ Fetched', allPreguntas.length, 'preguntas');
        commit("SET_PREGUNTAS", allPreguntas);
      } catch (err) {
        commit("SET_ERROR", err.message);
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async fetchRightBarPreguntas({ commit }) {
      let url = "/questions/";
      let allPreguntas = [];
      try {
        console.log('🔍 fetchRightBarPreguntas: Starting fetch...');
        console.log('🔍 Auth token exists:', !!localStorage.getItem('access_token'));
        if (localStorage.getItem('access_token')) {
          console.log('🔍 Auth token preview:', localStorage.getItem('access_token').substring(0, 20) + '...');
        }

        while (url) {
          console.log('🔍 Fetching URL:', url);
          const response = await axiosInstance.get(url);
          const data = response.data;

          console.log('📦 Response status:', response.status);
          console.log('📦 Questions received in this batch:', data.results?.length || 0);

          if (data && Array.isArray(data.results)) {
            // Check for PERSONAL questions
            const personalQuestions = data.results.filter(q =>
              q.category?.name?.toUpperCase() === 'PERSONAL'
            );
            console.log(`📊 PERSONAL questions in this batch: ${personalQuestions.length}`);
            if (personalQuestions.length > 0) {
              console.log('📋 PERSONAL questions titles:', personalQuestions.map(q => q.title));
            }

            allPreguntas = allPreguntas.concat(data.results);
            url = data.next;
          } else {
            throw new Error("Datos inválidos");
          }
        }

        const totalPersonal = allPreguntas.filter(q =>
          q.category?.name?.toUpperCase() === 'PERSONAL'
        ).length;
        console.log(`✅ Total questions fetched: ${allPreguntas.length}`);
        console.log(`✅ Total PERSONAL questions: ${totalPersonal}`);
        console.log(`📊 Questions by category:`,
          allPreguntas.reduce((acc, q) => {
            const cat = q.category?.name || 'Unknown';
            acc[cat] = (acc[cat] || 0) + 1;
            return acc;
          }, {})
        );

        commit("SET_RIGHTBAR_PREGUNTAS", allPreguntas);
      } catch (err) {
        console.error("❌ Error fetching rightbar questions:", err);
        console.error("❌ Error details:", err.response?.data || err.message);
      }
    },

    async fetchPreguntasForUser({ commit }) {
      commit("SET_LOADING", true);
      commit("SET_ERROR", null);
      let url = "/profiles/questions/";
      try {
        console.log('🔍 Fetching user questions from:', url);
        const response = await axiosInstance.get(url);
        console.log('📦 Response received:', response);
        const data = response.data;
        console.log('📊 Response data:', data);
        console.log('📊 Is Array?:', Array.isArray(data));
        console.log('📊 Data length:', data?.length);

        if (data && Array.isArray(data)) {
          console.log('✅ Committing SET_USER_PREGUNTAS with', data.length, 'items');
          commit("SET_USER_PREGUNTAS", data);
        } else {
          console.error('❌ Data is not an array:', typeof data, data);
          throw new Error("Datos inválidos");
        }
      } catch (err) {
        console.error('❌ Error in fetchPreguntasForUser:', err);
        commit("SET_ERROR", err.message);
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async voteForOption({ commit, dispatch }, payload) {
      console.log("Payload received in action:", payload);

      const { question_id, option_id, text_answer, profile_id, user_token, is_anonymous } =
        payload;

      console.log(
        "Extracted values - profileId:",
        profile_id,
        "questionId:",
        question_id,
        "optionId:",
        option_id,
        "textAnswer:",
        text_answer,
        "userToken:",
        user_token,
        "isAnonymous:",
        is_anonymous
      );

      // Validation: Must have question_id and (option_id OR text_answer)
      if (
        typeof question_id === "undefined" ||
        (typeof option_id === "undefined" && typeof text_answer === "undefined") ||
        (is_anonymous && !user_token)
      ) {
        console.error(
          "Error: questionId, optionId/textAnswer, or userToken is missing/invalid.",
          payload
        );
        return;
      }

      try {
        const postData = {
          question_id: question_id,
          option_id: option_id,
          text_answer: text_answer,
          is_anonymous: is_anonymous,
          user_token: user_token,
          profile_id: profile_id,
        };

        console.log("Dispatching voteForOption:", postData);

        const response = await axiosInstance.post(
          `/questions/${question_id}/vote/`,
          postData
        );

        console.log("Response from backend:", response.data);

        commit("UPDATE_VOTE", response.data.question);

        // Si el usuario está autenticado, actualizar sus datos y lista de votaciones
        if (!is_anonymous) {
          dispatch('fetchCurrentUser');
        }

        // Update global statistics in real-time
        dispatch('fetchGlobalStats');

      } catch (err) {
        console.error("Vote request error:", err.message);
        commit("SET_ERROR", err.message);
      }
    },

    async login({ commit, dispatch }, credentials) {
      console.log("Login credentials:", credentials); // Debugging login
      try {
        const response = await axiosInstance.post(
          "/profiles/login/",
          credentials
        );
        console.log("Login response:", response.data); // Debugging login response

        if (response.status === 200) {
          commit("SET_ACCESS_TOKEN", response.data.token.access);
          commit("SET_REFRESH_TOKEN", response.data.token.refresh);
          localStorage.setItem("access_token", response.data.token.access);
          localStorage.setItem("refresh_token", response.data.token.refresh);
          await dispatch("fetchCurrentUser");
          // fetchCurrentUser sets the user, so we can now fetch user questions
          await dispatch("fetchPreguntasForUser");
          router.push({ path: "/perfil", query: { tab: "personal" } });
        } else {
          throw new Error("Invalid login response");
        }
      } catch (err) {
        console.error("Login request error:", err.response || err.message);
        commit("SET_ERROR", err.response ? err.response.data : err.message);
        throw err; // Re-throw error so the component handles it
      }
    },

    async fetchUserProfile({ commit }, userId) {
      try {
        const response = await axiosInstance.get(`/profiles/${userId}/`);
        commit("SET_USER", response.data);
      } catch (error) {
        console.error("Error fetching user profile:", error);
        commit(
          "SET_ERROR",
          error.response ? error.response.data : error.message
        );
      }
    },

    async fetchProfiles({ commit }) {
      commit("SET_LOADING", true);
      try {
        const response = await axiosInstance.get("/profiles/");
        commit("SET_PROFILES_LIST", response.data.results || response.data);
      } catch (error) {
        console.error("Error fetching profiles:", error);
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async sendFriendRequest({ commit }, userId) {
      try {
        await axiosInstance.post(`/profiles/${userId}/friend-request/`);
        commit('UPDATE_PROFILE_STATUS', { id: userId, status: 'pending_sent' });
      } catch (error) {
        console.error("Error sending friend request:", error);
        throw error;
      }
    },

    async acceptFriendRequest({ commit }, userId) {
      try {
        await axiosInstance.post(`/profiles/${userId}/accept-friend/`);
        commit('UPDATE_PROFILE_STATUS', { id: userId, status: 'friends' });
      } catch (error) {
        console.error("Error accepting friend request:", error);
        throw error;
      }
    },

    async rejectFriendRequest({ commit }, userId) {
      try {
        await axiosInstance.post(`/profiles/${userId}/reject-friend/`);
        commit('UPDATE_PROFILE_STATUS', { id: userId, status: 'none' });
      } catch (error) {
        console.error("Error rejecting friend request:", error);
        throw error;
      }
    },

    async fetchFriendVotes({ commit }, userId) {
      commit("SET_LOADING", true);
      try {
        const response = await axiosInstance.get(`/profiles/${userId}/friend-votes/`);
        commit("SET_FRIEND_VOTES", response.data);
      } catch (error) {
        console.error("Error fetching friend votes:", error);
        // Clean previous votes
        commit("SET_FRIEND_VOTES", []);
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async updateProfile({ commit }, profileData) {
      try {
        const response = await axiosInstance.patch(
          "/profiles/update-profile/",
          profileData
        );
        commit("SET_USER", response.data);
        return response.data;
      } catch (error) {
        console.error("Error updating profile:", error);
        throw error;
      }
    },

    async fetchComments({ commit }, questionId) {
      try {
        const response = await axiosInstance.get(`/comments/?question=${questionId}`);
        commit('SET_COMMENTS', { questionId, comments: response.data.results || response.data });
      } catch (error) {
        console.error('Error fetching comments:', error);
      }
    },

    async postComment({ commit }, { questionId, text }) {
      const response = await axiosInstance.post('/comments/', {
        question: questionId,
        text
      });
      commit('ADD_COMMENT', response.data);
      return response.data;
    },

    async fetchCompatibility({ commit }) {
      commit("SET_LOADING", true);
      try {
        const response = await axiosInstance.get("/profiles/compatibility/");
        commit("SET_COMPATIBILITY_LIST", response.data);
      } catch (error) {
        console.error("Error fetching compatibility:", error);
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async fetchCompatibilityDetails({ commit }, { targetId, targetType }) {
      try {
        const response = await axiosInstance.get('/profiles/compatibility-details/', {
          params: { target_id: targetId, target_type: targetType }
        });
        return response.data;
      } catch (error) {
        console.error("Error fetching compatibility details:", error);
        throw error;
      }
    },

    async fetchCompatibility({ commit }) {
      commit("SET_LOADING", true);
      try {
        const response = await axiosInstance.get("/profiles/compatibility/");
        commit("SET_COMPATIBILITY_LIST", response.data);
      } catch (error) {
        console.error("Error fetching compatibility:", error);
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async fetchCompatibilityDetails({ commit }, { targetId, targetType }) {
      try {
        const response = await axiosInstance.get('/profiles/compatibility-details/', {
          params: { target_id: targetId, target_type: targetType }
        });
        return response.data;
      } catch (error) {
        console.error("Error fetching compatibility details:", error);
        throw error;
      }
    },

    async fetchCurrentUser({ commit }) {
      try {
        const response = await axiosInstance.get("/auth/user/");
        const user = response.data;
        // Normalize pk to id
        if (user.pk && !user.id) {
          user.id = user.pk;
        }
        console.log("Fetched Current User:", user);
        commit("SET_USER", user);
        return user;
      } catch (err) {
        console.error("Error fetching current user:", err);
      }
    },

    async register({ commit, dispatch }, userData) {
      try {
        const response = await axiosInstance.post(
          "/profiles/register/",
          userData
        );
        console.log("Register response:", response.data);
        commit("CLEAR_ERROR");

        // If registration returns unique token/key, log them in
        if (response.data.key || response.data.access) {
          const accessToken = response.data.key || response.data.access;
          commit("SET_ACCESS_TOKEN", accessToken);
          localStorage.setItem("access_token", accessToken);
          await dispatch("fetchCurrentUser");
        }

        return response.data;
      } catch (err) {
        console.error("Register request error:", err.response.data);
        commit("SET_ERROR", err.response.data);
        throw err.response.data;
      }
    },

    async checkAuthentication({ commit, dispatch }) {
      const token = localStorage.getItem("access_token");
      console.log("Checking authentication, token:", token); // Debugging token
      if (token) {
        try {
          await dispatch("fetchCurrentUser");
          await dispatch("fetchPreguntasForUser");
        } catch (error) {
          console.error("Authentication check failed:", error);
          commit("LOGOUT");
        }
      } else {
        console.log("No token found"); // Debugging no token case
      }
    },

    async socialLogin({ commit, dispatch }, { provider, accessToken }) {
      console.log(`${provider} login with token:`, accessToken);
      try {
        const response = await axiosInstance.post(
          `/auth/${provider}/`,
          { access_token: accessToken }
        );
        console.log("Social login response:", response.data);

        if (response.status === 200 && response.data) {
          // dj-rest-auth returns tokens in response.data
          const tokens = response.data;
          console.log("Social Auth Response Keys:", Object.keys(tokens));

          // Robustly find the token
          const accessToken = tokens.access || tokens.key || tokens.token;
          const refreshToken = tokens.refresh;

          if (!accessToken) {
            console.error("NO ACCESS TOKEN FOUND IN RESPONSE", tokens);
            throw new Error("No access token received from backend");
          }

          commit("SET_ACCESS_TOKEN", accessToken);
          if (refreshToken) {
            commit("SET_REFRESH_TOKEN", refreshToken);
            localStorage.setItem("refresh_token", refreshToken);
          }
          localStorage.setItem("access_token", accessToken);

          // Always fetch fresh user details from /auth/user/
          await dispatch("fetchCurrentUser");
          await dispatch("fetchPreguntasForUser");
          router.push("/");
        } else {
          throw new Error("Invalid social login response");
        }
      } catch (err) {
        console.error(`${provider} login request error:`, err.response ? JSON.stringify(err.response.data) : err.message);
        commit("SET_ERROR", err.response ? err.response.data : err.message);
        throw err;
      }
    },

    async updateProfile({ commit, state }, profileData) {
      if (!state.user || !state.user.id) return;
      try {
        const response = await axiosInstance.patch(`/profiles/${state.user.id}/`, profileData);
        commit("SET_USER", response.data);
      } catch (error) {
        console.error("Error updating profile:", error);
        throw error;
      }
    },

    async logout({ commit }) {
      try {
        commit("LOGOUT");
        router.push("/auth");
        // location.reload(); // Removed to prevent double loading/state issues, let logic handle clear
      } catch (error) {
        console.error("Error al cerrar sesión");
      }
    },

    async fetchCompatibility({ commit }) {
      try {
        const response = await axiosInstance.get('/profiles/compatibility/');
        commit('SET_COMPATIBILITY_LIST', response.data);
        return response.data;
      } catch (error) {
        console.error('Error fetching compatibility:', error);
        return [];
      }
    },

    async fetchCompatibilityDetails({ commit }, { targetId, targetType }) {
      try {
        const response = await axiosInstance.get(`/profiles/${targetId}/compatibility-details/`);
        return response.data;
      } catch (error) {
        console.error('Error fetching compatibility details:', error);
        return [];
      }
    },

    async toggleQuestionPrivacy({ commit }, questionId) {
      try {
        const response = await axiosInstance.post('/answers/toggle-privacy/', { question_id: questionId });
        return response.data;
      } catch (error) {
        console.error("Error toggling privacy:", error);
        throw error;
      }
    },

    async toggleQuestionPrivacy({ commit }, questionId) {
      try {
        const response = await axiosInstance.post('/answers/toggle-privacy/', { question_id: questionId });
        // Optionally update local state if needed (handled by re-fetch usually)
        return response.data;
      } catch (error) {
        console.error("Error toggling privacy:", error);
        throw error;
      }
    },

    async fetchGlobalStats({ commit }) {
      try {
        const response = await axiosInstance.get('/questions/statistics/');
        commit('SET_GLOBAL_STATS', response.data);
      } catch (error) {
        console.error('Error fetching global stats:', error);
      }
    },

    async rateQuestion({ commit }, { questionId, score }) {
      try {
        const response = await axiosInstance.post(`/questions/${questionId}/rate/`, { score });
        commit('UPDATE_QUESTION_RATING', {
          questionId,
          ratingAverage: response.data.rating_average,
          ratingCount: response.data.rating_count,
          userRating: response.data.user_rating
        });
        return response.data;
      } catch (error) {
        console.error('Error rating question:', error);
        throw error;
      }
    },

    async fetchQuestionsByCategory({ commit }, category) {
      try {
        console.log("🛒 Action fetchQuestionsByCategory called for:", category);
        commit('SET_LOADING', true);
        const url = `/questions/?category__name=${category}`;
        console.log("🔗 Fetching URL:", url);
        const response = await axiosInstance.get(url);
        console.log("📥 API Response status:", response.status);
        console.log("📥 API Response data length:", response.data.results ? response.data.results.length : response.data.length);
        const questions = response.data.results || response.data;
        return questions;
      } catch (error) {
        console.error("❌ Error fetching questions category:", error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async deleteVote({ commit, dispatch, state }, { questionId }) {
      try {
        const response = await axiosInstance.post('/answers/delete-vote/', { question_id: questionId });

        // Optimistically update state to remove vote immediately
        // Find question and clear its current_user_answer
        const question = state.preguntas.find(q => q.id === questionId);
        if (question) {
          // We need a mutation to reactively update this deep property
          commit('REMOVE_USER_VOTE', questionId);
        }

        // Refresh data
        dispatch('fetchCurrentUser');
        dispatch('fetchGlobalStats'); // Update global stats charts
        dispatch('fetchPreguntas'); // Refresh global question list counts
        dispatch('fetchPreguntasForUser'); // Refresh user specific list

        return response.data;
      } catch (error) {
        console.error("Error deleting vote:", error);
        throw error;
      }
    },

    async submitAnswer({ commit, dispatch }, { questionId, optionId, textAnswer }) {
      try {
        const payload = {};
        if (optionId) payload.option_id = optionId;
        if (textAnswer) payload.text_answer = textAnswer;

        const response = await axiosInstance.post(`/questions/${questionId}/vote/`, payload);
        return response.data;
      } catch (error) {
        console.error("Error submitting answer:", error);
        throw error;
      }
    },
  },

  getters: {
    preguntas: (state) => state.preguntas,
    rightBarPreguntas: (state) => state.rightBarPreguntas,
    loading: (state) => state.loading,
    error: (state) => state.error,
    isAuthenticated: (state) => !!state.accessToken,
    user: (state) => state.user,
    profilesList: (state) => state.profilesList,
  },
});

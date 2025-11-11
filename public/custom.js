(async function () {
  console.log("🔐 Custom JS loaded!");

  // try {
  //   // FastAPI에서 에페메럴 토큰 요청
  //   const res = await fetch("/auth/ephemeral", {
  //     credentials: "include" // 쿠키 포함
  //   });

  //   console.log(res)
  //   if (!res.ok) {
  //     console.warn("❌ Failed to get ephemeral token. Redirecting to login...");
  //     alert("로그인이 필요합니다. /login 으로 이동합니다.");
  //     // window.location.href = "/";
  //     // return;
  //   } else {
  //      const data = await res.json();
  //     const ephemeralToken = data.result;

  //     console.log("✅ Received ephemeral token:", ephemeralToken);

  //     // Chainlit 클라이언트 세션에 토큰 주입
  //     window.cl_user_session = { token: ephemeralToken };
  //   }

   

  // } catch (err) {
  //   console.error("Error fetching ephemeral token:", err);
  // }
})();

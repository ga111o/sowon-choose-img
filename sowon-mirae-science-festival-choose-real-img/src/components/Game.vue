<template>
  <center>
    <div>
      <div v-if="!submitted">
        <form @submit.prevent="startGame">
          <div
            style="
              display: flex;
              justify-content: space-around;
              margin-bottom: 20px;
            "
          >
            <select v-model="age" required>
              <option value="" disabled selected>나이 선택</option>
              <option
                v-for="year in Array.from({ length: 30 }, (v, k) => k)"
                :key="year + 1"
                :value="year + 1"
              >
                {{ year + 1 }}살
              </option>
            </select>

            <div class="gender-label-box">
              <label class="gender-label">
                <input type="radio" value="남자" v-model="gender" required />
                남자
              </label>
              <label class="gender-label">
                <input type="radio" value="여자" v-model="gender" required />
                여자
              </label>
            </div>
          </div>

          <div>
            전화번호:
            <input
              v-model="phonePart1"
              required
              minlength="3"
              maxlength="3"
              value="010"
            />
            -
            <input v-model="phonePart2" required minlength="4" maxlength="4" />
            -
            <input v-model="phonePart3" required minlength="4" maxlength="4" />
          </div>

          <div>
            <label>
              <details>
                <summary>개인정보 수집 동의</summary>
                <p>
                  상품 발송을 위한 나이, 성별, 전화번호 수집에 동의가
                  필요합니다.
                </p>
                <p>
                  전화번호는 상품 발송 이후 즉시 파기되며, 나이와 성별은 실제
                  인간의 사진과 인공지능이 생성한 사진을 구분하는 능력을
                  평가하는 연구에 사용됩니다.
                </p>
              </details>
              <input type="checkbox" required />
              개인정보 수집에 동의합니다.
            </label>
          </div>

          <div class="difficulty-label-box">
            <label class="difficulty-label"> 난이도:</label>
            <label class="difficulty-label">
              <input type="radio" value="easy" v-model="difficulty" required />
              보통
            </label>
            <label class="difficulty-label">
              <input type="radio" value="여자" v-model="difficulty" required />
              어려움
            </label>
          </div>
          <button type="submit">게임 시작</button>
        </form>
      </div>

      <div v-else class="box">
        <div v-if="feedbackMessage" class="feedback">{{ feedbackMessage }}</div>
        <div class="images">
          <img
            v-for="(image, index) in images"
            :key="index"
            :src="image"
            @click="imageClicked(image)"
            class="image-item"
          />
        </div>
        <h3 class="score">점수: {{ score }}</h3>
        <button v-if="showNextButton" @click="nextStage" class="next-button">
          다음 이미지 보기
        </button>
      </div>
    </div>
  </center>
</template>

<script>
export default {
  name: "ImageSelectionGame",
  data() {
    return {
      age: "",
      gender: "",
      phonePart1: "010",
      phonePart2: "",
      phonePart3: "",
      images: [],
      feedbackMessage: "",
      score: 0,
      submitted: false,
      currentStage: 0,
      maxStages: 6,
      showNextButton: false,
      usedImages: [],
      imageClickable: true,
      startTime: null,
      elapsedTime: 0,
      difficulty: "easy",
    };
  },
  methods: {
    startGame() {
      this.phone = `${this.phonePart1}-${this.phonePart2}-${this.phonePart3}`;
      this.submitted = true;
      this.currentStage = 0;
      this.usedImages = [];
      this.loadImages();
    },
    loadImages() {
      const realImages = this.loadImagesFromFolder(
        require.context("@/assets/images/real", false, /\.(png|jpe?g|gif)$/)
      );

      const easyImages = this.loadImagesFromFolder(
        require.context(
          "@/assets/images/generated/easy",
          false,
          /\.(png|jpe?g|gif)$/
        )
      );

      const hardImages = this.loadImagesFromFolder(
        require.context(
          "@/assets/images/generated/hard",
          false,
          /\.(png|jpe?g|gif)$/
        )
      );

      let selectedRealImages, selectedOtherImages;

      do {
        selectedRealImages = this.getRandomImages(realImages, 1);
        selectedOtherImages = this.getRandomImages(
          this.difficulty === "easy" ? easyImages : hardImages,
          1
        );
      } while (
        this.usedImages.includes(selectedRealImages[0]) ||
        this.usedImages.includes(selectedOtherImages[0])
      );

      console.log("점수", this.score);

      if (this.score % 2 === 0) {
        this.images = [...selectedOtherImages, ...selectedRealImages];
      } else {
        this.images = [...selectedRealImages, ...selectedOtherImages];
      }

      this.startTime = Date.now();

      this.usedImages.push(...this.images);
      this.showNextButton = false;
    },
    loadImagesFromFolder(context) {
      return context.keys().map((key) => context(key));
    },

    getRandomImages(images, count) {
      const shuffled = this.shuffleArray([...images]);
      return shuffled.slice(0, count);
    },

    shuffleArray(array) {
      for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
      }
      return array;
    },
    imageClicked(image) {
      if (!this.imageClickable) return;

      this.imageClickable = false;

      const isEvenScore = this.score % 2 === 0;
      const selectedRealImage = this.images[0];
      const selectedGeneratedImage = this.images[1];

      const isRealImage =
        (isEvenScore && image === selectedGeneratedImage) ||
        (!isEvenScore && image === selectedRealImage);
      this.elapsedTime = ((Date.now() - this.startTime) / 1000).toFixed(3);

      if (isRealImage) {
        this.score++;
        this.feedbackMessage = "정답입니다!";
        this.submitScore(
          selectedRealImage,
          selectedGeneratedImage,
          this.elapsedTime,
          true
        );
      } else {
        this.feedbackMessage = "오답...";
        this.submitScore(
          selectedRealImage,
          selectedGeneratedImage,
          this.elapsedTime,
          false
        );
      }

      this.showNextButton = true;
    },

    nextStage() {
      this.imageClickable = true;

      if (this.currentStage < this.maxStages - 1) {
        this.currentStage++;
        this.feedbackMessage = "";
        this.loadImages();
      } else {
        this.fetchScore(this.phone, this.age, this.gender);
        alert("축하드려요! " + this.score);
        this.resetGame();
      }
    },

    resetGame() {
      this.age = "";
      this.gender = "";
      this.phonePart1 = "010";
      this.phonePart2 = "";
      this.phonePart3 = "";
      this.images = [];
      this.feedbackMessage = "";
      this.score = 0;
      this.submitted = false;
      this.currentStage = 0;
      this.maxStages = 6;
      this.showNextButton = false;
      this.usedImages = [];
      this.imageClickable = true;
      this.startTime = null;
      this.elapsedTime = 0;
    },

    submitScore(realImage, generatedImage, elapsedTime, isCorrect) {
      const realImageName = realImage.split("/").pop();
      const generatedImageName = generatedImage.split("/").pop();

      const data = {
        age: this.age,
        gender: this.gender,
        phone: this.phone,
        score: this.score,
        realImage: realImageName,
        generatedImage: generatedImageName,
        elapsedTime: elapsedTime,
        isCorrect: isCorrect,
      };

      console.log(data);

      fetch("http://localhost:8000/save/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
        })
        .catch((error) => {
          console.error("server error:", error);
        });
    },

    fetchScore(phone, age, gender) {
      const data = {
        phone: phone,
        age: parseInt(age, 10),
        gender: gender,
      };

      fetch("http://localhost:8000/fetch_score/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
        })
        .catch((error) => {
          console.error("server error:", error);
        });
    },
  },
};
</script>

<style scoped>
.box {
  width: 700px;
}

.feedback {
  font-size: 30px;
  font-weight: bold;
  margin-bottom: 20px;
}

.images {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: space-around;
}

.image-item {
  cursor: pointer;
  border: 2px solid #ccc;
  border-radius: 5px;
  transition: transform 0.2s;
}

.image-item:hover {
  transform: scale(1.05);
}

.score {
  font-size: 25px;
  margin-top: 20px;
  margin-top: 30px;
}

.next-button {
  background-color: #8a1601;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: 0.3s;
}

.next-button:hover {
  background-color: #581004;
  box-shadow: 0 1px 15px #601b0f5c;
}

body {
  font-family: Arial, sans-serif;
  background-color: #f9f9f9;
  padding: 20px;
}

form {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  max-width: 400px;
  margin: auto;
}

select {
  width: 40%;
  padding: 10px;
  margin: 0 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
}

input {
  width: 15%;
  padding: 10px;
  margin-bottom: 15px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
}

input[type="checkbox"] {
  width: 20px;
  padding: 10px;
  margin-bottom: 15px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
  height: 20px;
}

select:focus,
input:focus {
  border-color: #8a1601;
  outline: none;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #8a1601;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: 0.3s;
}

button:hover {
  background-color: #581004;
  box-shadow: 0 1px 15px #601b0f5c;
}

label {
  display: block;
  margin-bottom: 10px;
}

details {
  margin-top: 10px;
}

summary {
  cursor: pointer;
  font-weight: bold;
}

input[type="checkbox"] {
  margin: 10px 5px 10px 0;
}

input[type="radio"] {
  width: 30px;
  margin: 0;
}

.gender-label-box {
  display: flex;
  align-items: center;
  font-size: 18px;
}

.gender-label {
  margin: 0 15px 0 0;
}

.difficulty-label-box {
  display: flex;
  width: 300px;
  align-items: center;
  justify-content: space-evenly;
  font-size: 18px;
}

.difficulty-label {
  margin: 30px 0 20px 0;
}
</style>

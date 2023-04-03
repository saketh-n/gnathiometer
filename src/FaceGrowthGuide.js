import React, { useState } from "react";
import axios from "axios";
import "./FaceGrowthGuide.css";

const FaceGrowthGuide = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [resultImage, setResultImage] = useState(null);

  const onFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const onFileUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("image", selectedFile);

    try {
      const response = await axios.post(
        "http://localhost:5000/api/process-image",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setResultImage(response.data);
      console.log(response.data);
    } catch (error) {
      console.error("Error uploading and processing image:", error);
    }
  };

  return (
    <div>
      <h2>Face Growth Guide</h2>
      <input type="file" onChange={onFileChange} />
      <button onClick={onFileUpload}>Upload and Process</button>
      {resultImage && (
        <img
          className="processedImage"
          src={resultImage}
          alt="Processed image"
        />
      )}
    </div>
  );
};

export default FaceGrowthGuide;

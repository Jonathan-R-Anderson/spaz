import { useEffect } from "react";

interface IndexProps {
  targetPath: string;
}

const Index: React.FC<IndexProps> = ({ targetPath }) => {
  useEffect(() => {
    window.location.href = targetPath;
  }, [targetPath]);

  return null;
};

export default Index;

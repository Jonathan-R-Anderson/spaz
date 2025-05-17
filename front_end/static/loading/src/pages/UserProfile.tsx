import { useParams } from "react-router-dom";

const UserProfile = () => {
  const { eth_address } = useParams();

  return (
    <div className="user-profile">
      <h1>User Profile</h1>
      <p>Ethereum Address: {eth_address}</p>
    </div>
  );
};

export default UserProfile;

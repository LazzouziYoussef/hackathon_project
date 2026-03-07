import axios from 'axios'
const getMetrics =()=>{
axios.get("http://localhost:5173/metrics").then(res =>{
  console.log(res);
}).catch( err =>{
  console.log(err)
})
}
const UseMetrics = () => {
  return (
    <div onClick={getMetrics}>getMetrics</div>
  )
}

export default UseMetrics
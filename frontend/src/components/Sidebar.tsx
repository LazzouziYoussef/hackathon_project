
import { NavLink } from 'react-router-dom'




const Sidebar = () => {
  const pages = [
    {name:"Dashboard" ,path:"/Dashboard"},
    {name:"Projects",path:"/Projects"}
  ]
  return (
<>
<aside className="fixed w-64 h-full">
        <h2 className="text-2xl font-bold mb-10">
          Sadaqa <span className="font-light text-indigo-400">Tech</span>
        </h2>
          {pages.map((page)=>(
            <NavLink key={page.name} to={page.path}
            className="flex flex-col"
            >
              {page.name}
            </NavLink>
          ))}
       
      </aside>
</>
)
}

export default Sidebar
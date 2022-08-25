import React from "react";
import { Nav, NavLink, NavMenu }
    from "./NavbarElements";

const Navbar = () => {
  return (
    <>
      <Nav>
        <NavMenu>
          <NavLink to="/knowledgedailydigest" activeStyle>
            Knowledge Daily Digest
          </NavLink>
        </NavMenu>
      </Nav>
    </>
  );
};

export default Navbar;

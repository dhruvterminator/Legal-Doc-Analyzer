import { Container, Row, Col, Tab, Nav } from "react-bootstrap";
import { ProjectCard } from "./projectCard";
import projImg1 from "../assets/img/project-img1.png";
import projImg2 from "../assets/img/project-img2.png";
import projImg3 from "../assets/img/project-img3.png";
import colorSharp2 from "../assets/img/color-sharp2.png";
import 'animate.css';
import TrackVisibility from 'react-on-screen';

export const Projects = () => {

  const projects = [
    {
      title: "Dhruv Gupta",
      description: "Software Engineer",
      imgUrl: "https://media.licdn.com/dms/image/v2/D5635AQFwtA9qvFw3eg/profile-framedphoto-shrink_200_200/B56Zl4PKfbG0AY-/0/1758658865590?e=1766264400&v=beta&t=CfIGjdBFAjZYh-LRshEYNfJLpniwPgyQ6kxVkbdnMYM",
    },
    {
      title: "Pankaj Sharma",
      description: "Software Engineer",
      imgUrl: "",
    },
    {
      title: "Aditi Sharma",
      description: "Software Engineer",
      imgUrl: "",
    },
    {
      title: "Shanvee MAurya",
      description: "Software Engineer",
      imgUrl: "",
    },
  ];

  return (
    <section className="project" id="dev">
      <Container>
        <Row>
          <Col sm={12}>
            <TrackVisibility>
              {({ isVisible }) =>
              <div className={isVisible ? "animate__animated animate__fadeIn" : ""}>
                <h2>Who we are ?</h2>
                <p>Our projects have been brought to life with the assistance of a diverse group of skilled KIET students. These talented individuals have contributed their expertise, passion, and dedication to crafting innovative solutions that meet the needs of our clients and users.</p>
                <Tab.Container id="projects-tabs" defaultActiveKey="first">
                  {/* <Nav variant="pills" className="nav-pills mb-5 justify-content-center align-items-center" id="pills-tab">
                    <Nav.Item>
                      <Nav.Link eventKey="first">Tab 1</Nav.Link>
                    </Nav.Item>
                    <Nav.Item>
                      <Nav.Link eventKey="second">Tab 2</Nav.Link>
                    </Nav.Item>
                    <Nav.Item>
                      <Nav.Link eventKey="third">Tab 3</Nav.Link>
                    </Nav.Item>
                  </Nav> */}
                  <Tab.Content id="slideInUp" className={isVisible ? "animate__animated animate__slideInUp" : ""}>
                    <Tab.Pane eventKey="first">
                      <Row>
                        {
                          projects.map((project, index) => {
                            return (
                              <ProjectCard
                                key={index}
                                {...project}
                              />
                            )
                          })
                        }
                      </Row>
                    </Tab.Pane>
                    {/* <Tab.Pane eventKey="second">
                      <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Cumque quam, quod neque provident velit, rem explicabo excepturi id illo molestiae blanditiis, eligendi dicta officiis asperiores delectus quasi inventore debitis quo.</p>
                      <div className="proj-imgbx">
                        <img src="https://i.postimg.cc/MKLWyhdb/IMG-20230422-075421.jpg" alt="Project Image" />
                        <div className="proj-txtx">
                          <h4>Oussama Louati</h4>
                          <span>software Engineer</span>
                        </div>
                      </div>
                    </Tab.Pane>
                    <Tab.Pane eventKey="third">
                      <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Cumque quam, quod neque provident velit, rem explicabo excepturi id illo molestiae blanditiis, eligendi dicta officiis asperiores delectus quasi inventore debitis quo.</p>
                    </Tab.Pane> */}
                  </Tab.Content>
                </Tab.Container>
              </div>}
            </TrackVisibility>
          </Col>
        </Row>
      </Container>
      {/* <img className="background-image-right" src="https://i.postimg.cc/Gp5qSPks/Untitled-design-3.png" alt=""></img> */}
    </section>
  )
}

import React, { useEffect } from 'react';
import logo from './logo.svg';
import './App.css';
import { Box, Button, Card, CardActionArea, CardActions, CardContent, Container, Divider, Grid, LinearProgress, Paper, Snackbar, TextField, ThemeProvider, Typography, styled } from '@mui/material';
import { Timeline, TimelineConnector, TimelineContent, TimelineDot, TimelineItem, TimelineOppositeContent, TimelineSeparator } from '@mui/lab';
import {
  timelineOppositeContentClasses,
} from '@mui/lab/TimelineOppositeContent';
import {
  timelineContentClasses
} from '@mui/lab/TimelineContent';

// Environment
const env = process.env.NODE_ENV || 'development'

const APIList = [
  {
    name: "Hydro",
    description: "Hydro OJ's Homework, using ShanghaiTech ACM",
    formdata: [
      {
        name: "username",
        type: "text",
      },
      {
        name: "password",
        type: "password",
      }
    ],
    api: "/api/hydro",
  },
  {
    name: "Gradescope",
    description: "Gradescope assignments, based on gradescope-tool",
    formdata: [
      {
        name: "email",
        type: "email",
      },
      {
        name: "password",
        type: "password",
      }
    ],
    api: "/api/gradescope",
  },
  {
    name: "Blackboard",
    description: "ShanghaiTech blackboard",
    formdata: [
      {
        name: "studentid",
        type: "text",
      },
      {
        name: "password",
        type: "password",
      }
    ],
    api: "/api/blackboard",
  },
]

function App() {

  const [isLoading, setIsLoading] = React.useState(APIList.map(() => false))
  const [data, setData] = React.useState<any[]>(localStorage.getItem('data') ? JSON.parse(localStorage.getItem('data') as string) : [])
  const [error, setError] = React.useState("")
  const [open, setOpen] = React.useState(false)
  const [showForm, setShowForm] = React.useState(localStorage.getItem('showForm') === 'false' ? false : true)

  const fetchData = async () => {
    APIList.forEach((item) => {
      item.formdata.forEach((formitem) => {
        const value = (document.getElementById(`${item.name}-${formitem.name}`) as HTMLInputElement).value
        localStorage.setItem(`${item.name}-${formitem.name}`, value)
      })
    })

    var tmpData = [] as any[];

    Promise.all(APIList.map(async (item) => {
      setIsLoading(isLoading => isLoading.map((value, index) => index === APIList.indexOf(item) ? true : value))
      var postData = {} as any;
      var flag = true;
      item.formdata.forEach((formitem) => {
        const value = localStorage.getItem(`${item.name}-${formitem.name}`)
        if(value === null || value === "" || value === undefined) {
          setIsLoading(isLoading => isLoading.map((value, index) => index == APIList.indexOf(item) ? false : value))
          flag = false;
        }
        postData[formitem.name] = value;
      })

      return flag? fetch(
        (env == "development" ? "http://localhost:5000" : "") + item.api,
        {
          method: 'POST',
          body: JSON.stringify(postData),
          headers: {
            'Content-Type': 'application/json'
          }
        })
        .then(res => {
          setIsLoading(isLoading => isLoading.map((value, index) => index == APIList.indexOf(item) ? false : value))
          return res.json()
        })
        .catch(error => {
          console.error(error);
          setError(`${item.name} : ${error}`);
          setIsLoading(isLoading => isLoading.map((value, index) => index == APIList.indexOf(item) ? false : value))
        }) : null;
    }))
      .then(result => {
        // console.log(result)
        for (let i = 0; i < result.length; i++) {
          if (!result[i]) continue;
          if (result[i].status == "success") {
            for (let j = 0; j < result[i].data.length; j++) {
              if (!result[i].data[j].submitted)
                tmpData.push(result[i].data[j])
            }
          }
        }
      })
      .finally(() => {
        tmpData.sort((a, b) => a.due - b.due)
        setData(tmpData)
        localStorage.setItem('data', JSON.stringify(tmpData))
        setIsLoading(isLoading => isLoading.map(() => false))
      })
  }

  const onSaveClick = (index: number) => {
    const item = APIList[index]
    item.formdata.forEach((formitem) => {
      const value = (document.getElementById(`${item.name}-${formitem.name}`) as HTMLInputElement).value
      localStorage.setItem(`${item.name}-${formitem.name}`, value)
    })
    // fetchData()
  }

  useEffect(() => {
    fetchData()
  }, [])

  useEffect(() => {
    setOpen(error !== "")
  }, [error])

  return (
    <div className="App">
      <Container component="main" maxWidth="xl">
        <Snackbar
          open={open}
          autoHideDuration={2000}
          onClose={() => setOpen(false)}
          message={error.toString()}
        />

        <Grid
          container spacing={{ xs: 2, md: 3 }}
          columns={{ xs: 1, sm: 2, md: 2 }}
          direction="row"
          justifyContent="center"
          sx={{
            pt: 8, pb: 2,
          }}
        >
          <Grid item xs={1}>
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
              }}
            >
              <img src="LOGO.png" alt="logo" width="200" height="200" />
              <Typography variant="h2" component="h1">Holly DDL</Typography>
              <Typography variant="h5" component="span" gutterBottom>Check your DDL in one site</Typography>


              <Button
                variant='contained'
                color='primary'
                fullWidth
                sx={{ mt: 2, mb: 1 }}
                onClick={fetchData}
                disabled={isLoading.some((value) => value)}
              >Login & Fetch</Button>

              <Button
                variant={showForm ? 'contained' : 'outlined'}
                onClick={() => { setShowForm(!showForm); localStorage.setItem('showForm', showForm ? 'false' : 'true') }}
                sx={{ mt: 1, mb: 2 }}
                fullWidth
              >{showForm ? 'Hide' : 'Show'} Login Form</Button>

              <Grid
                container spacing={{ xs: 2, md: 3 }}
                columns={{ xs: 4, sm: 4, md: 8, lg: 12 }}
                direction="row"
                justifyContent="center"
                alignItems="center"
                sx={{
                  display: showForm ? 'flex' : 'none',
                }}
              >
                {APIList.map((item, index) => (
                  <Grid item xs={4} sm={4} md={4} key={index}>
                    <Card elevation={2}>
                      <CardContent>
                        <Typography variant="h5" component="div" align='left'>
                          Login into <code>{item.name}</code>
                        </Typography>
                        <Typography variant="body2" align='left'>
                          {item.description}
                        </Typography>
                        {/* <Box component="form" onSubmit={() => { }} noValidate sx={{ mt: 1 }}>
                      
                    </Box> */}
                        {item.formdata && item.formdata.map((formitem, formindex) => (
                          <TextField
                            key={formindex}
                            margin="normal"
                            required
                            fullWidth
                            id={`${item.name}-${formitem.name}`}
                            label={formitem.name.toUpperCase()}
                            name={`${item.name}-${formitem.name}`}
                            type={formitem.type}
                            autoComplete={`${item.name}-${formitem.name}`}
                            defaultValue={localStorage.getItem(`${item.name}-${formitem.name}`) || ""}
                          />))}
                      </CardContent>
                      <CardActions>
                        {isLoading[index] ? (<LinearProgress sx={{ width: '100%' }} />) : (<></>)}
                        {/* <Button onClick={() => {onSaveClick(index)}}>Save</Button> */}
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          </Grid>

          <Grid item xs={1}>
            <Paper elevation={3} sx={{ padding: 2, overflow: "auto" }}>
              <Typography variant="h4" component="h1" gutterBottom>Your DDLs</Typography>
              <Divider />
              <Timeline
                sx={{
                  [`& .${timelineOppositeContentClasses.root}`]: {
                    flex: 0.2,
                  },
                }}
              >
                {data.map((item, index) => (
                  <TimelineItem>
                    <TimelineOppositeContent color="text.secondary" sx={{ minWidth: '60px', pl: 0, fontSize: '10pt' }}>
                      {new Date(Number(item.due) * 1000).toLocaleString()}
                    </TimelineOppositeContent>
                    <TimelineSeparator>
                      <TimelineDot color={item.due > Date.now() / 1000 ? "primary" : "grey"} />
                      <TimelineConnector />
                    </TimelineSeparator>
                    <TimelineContent>
                      <Typography variant="h6" component="h1" sx={{ wordBreak: "break-word" }}>{item.title}</Typography>
                      <Typography variant="body1" component="p" color="text.secondary">{item.course}</Typography>
                      <Typography variant="body2" component="p" color="text.secondary">
                        Status: {item.status}
                      </Typography>
                      <a href={item.url} target="_blank" rel="noreferrer">Detail</a>
                    </TimelineContent>
                  </TimelineItem>
                ))}
              </Timeline>
            </Paper>
          </Grid>
        </Grid>
      </Container>
      <img src={"https://ipacel.cc/+/MoeCounter2/?name=hollyddl"} />
    </div >
  );
}

export default App;

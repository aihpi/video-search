import React, { useEffect, useState, createContext, useContext } from "react";
import {
  Box,
  Button,
  Container,
  Flex,
  Input,
  DialogBody,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
  Stack,
  Text,
  DialogActionTrigger,
} from "@chakra-ui/react";

interface Upload {
  id: string;
  item: string;
}

const UploadContext = createContext({
  upload: [], fetchUploads: () => {}
})

export default function Uploads() {
  const [uploads, setUploads] = useState([])
  const fetchUploads = async () => {
    const response = await fetch("http://localhost:8000/upload")
    const uploads = await response.json()
    setUploads(uploads.data)
  }
}

useEffect(() => {
  fetchUploads()
}, [])

return (
  <UploadsContext.Provider value={{uploads, fetchUploads}}>
    <Container maxW="container.xl" pt="100px">
      <Stack gap={5}>
        {uploads.map((upload: Upload) => (
          <b key={upload.id}>{upload.item}</b>
        ))}
      </Stack>
    </Container>
  </UploadsContext.Provider>
)
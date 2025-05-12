import { ChakraProvider } from '@chakra-ui/react'
import { defaultSystem } from "@chakra-ui/react"
import Header from "./components/Header";
import Uploads from "./components/Upload";

function App() {

  return (
    <ChakraProvider value={defaultSystem}>
      <Header />
      <Uploads /> 
    </ChakraProvider>
  )
}

export default App;
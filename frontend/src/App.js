import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ChakraProvider, Box, VStack, Text, Input, Button, Flex, Spinner } from '@chakra-ui/react';

function App() {
  const [input, setInput] = useState('');
  const [conversation, setConversation] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    console.log('isLoading state changed:', isLoading);
  }, [isLoading]);

  const handleAsk = async () => {
    console.log('handleAsk function called');
    setIsLoading(true);
    console.log('Setting isLoading to true');

    try {
      console.log('Sending request to backend');
      const response = await axios.post('http://localhost:8000/ask', {
        text: input,
        conversation_history: conversation
      });
      console.log('Full response from backend:', response);
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);
      console.log('Response data:', response.data);
      if (response.data && response.data.answer) {
        const newConversation = [
          ...conversation,
          { type: 'user', text: input },
          { type: 'bot', text: response.data.answer }
        ];
        console.log('New conversation before state update:', newConversation);
        setConversation(newConversation);
        setInput('');
        console.log('Updated conversation state:', newConversation);
        setTimeout(() => {
          console.log('Conversation state after update:', conversation);
        }, 0);
      } else {
        console.error('Unexpected response format:', response.data);
        setConversation([
          ...conversation,
          { type: 'user', text: input },
          { type: 'bot', text: 'Received an unexpected response format from the server.' }
        ]);
      }
    } catch (error) {
      console.error('Error asking question:', error);
      if (error.response) {
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
        console.error('Error response headers:', error.response.headers);
      } else if (error.request) {
        console.error('No response received. Request details:', error.request);
      } else {
        console.error('Error setting up request:', error.message);
      }
      console.error('Error config:', error.config);
      setConversation([
        ...conversation,
        { type: 'user', text: input },
        { type: 'bot', text: 'Sorry, there was an error processing your question. Please try again.' }
      ]);
    } finally {
      setIsLoading(false);
      console.log('Setting isLoading to false');
    }
  };

  return (
    <ChakraProvider>
      <Box maxWidth="800px" margin="auto" padding={8}>
        <VStack spacing={4} align="stretch">
          <Text fontSize="2xl" fontWeight="bold">Chatbot for Document Q&A</Text>
          <Box height="400px" overflowY="auto" borderWidth={1} borderRadius="lg" padding={4}>
            {conversation.length === 0 ? (
              <Text color="gray.500">No messages yet. Start a conversation!</Text>
            ) : (
              conversation.map((message, index) => (
                <Flex key={index} marginY={2} flexDirection={message.type === 'user' ? 'row-reverse' : 'row'}>
                  <Box
                    maxWidth="70%"
                    backgroundColor={message.type === 'user' ? 'blue.100' : 'gray.100'}
                    padding={2}
                    borderRadius="lg"
                  >
                    <Text>{message.text}</Text>
                  </Box>
                </Flex>
              ))
            )}
          </Box>
          <Input
            placeholder="Ask a question about the document"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAsk()}
          />
          <Flex alignItems="center" justifyContent="flex-start">
            <Button
              onClick={handleAsk}
              colorScheme="blue"
              isDisabled={isLoading}
              mr={2}
            >
              Ask
            </Button>
            {isLoading && (
              <Flex alignItems="center">
                <Spinner size="sm" color="blue.500" mr={2} />
                <Text>Processing...</Text>
              </Flex>
            )}
          </Flex>
        </VStack>
      </Box>
    </ChakraProvider>
  );
}

export default App;

#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::string text, long chunks) {
    std::vector<std::string> result;
    std::istringstream iss(text);
    std::string line;
    
    while (std::getline(iss, line)) {
        result.push_back(line);
    }
    
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("/alcm@ an)t//eprw)/e!/d\nujv"), (0)) == (std::vector<std::string>({(std::string)"/alcm@ an)t//eprw)/e!/d", (std::string)"ujv"})));
}

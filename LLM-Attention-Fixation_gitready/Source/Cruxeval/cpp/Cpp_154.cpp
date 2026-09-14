#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, std::string c) {
    std::istringstream iss(s);
    std::vector<std::string> tokens;
    std::string token;
    while (std::getline(iss, token, ' ')) {
        tokens.push_back(token);
    }
    std::reverse(tokens.begin(), tokens.end());
    
    std::string result = c + "  ";
    for (size_t i = 0; i < tokens.size(); ++i) {
        if (i != 0) {
            result += "  ";
        }
        result += tokens[i];
    }

    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("Hello There"), ("*")) == ("*  There  Hello"));
}

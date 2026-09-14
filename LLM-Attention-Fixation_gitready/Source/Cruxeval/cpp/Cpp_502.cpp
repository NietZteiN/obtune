#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string name) {
    std::stringstream ss;
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream tokenStream(name);

    while (std::getline(tokenStream, token, ' ')) {
        tokens.push_back(token);
    }

    for (int i = 0; i < tokens.size(); i++) {
        ss << tokens[i];
        if (i != tokens.size() - 1) {
            ss << "*";
        }
    }

    return ss.str();
}
int main() {
    auto candidate = f;
    assert(candidate(("Fred Smith")) == ("Fred*Smith"));
}

#include <assert.h>
#include <bits/stdc++.h>
bool f(std::string text, std::string delimiter) {
    if (text.find(delimiter) != std::string::npos) {
        std::vector<std::string> tokens;
        std::istringstream iss(text);
        std::string token;
        while (std::getline(iss, token, delimiter[0])) {
            if (!token.empty()) {
                tokens.push_back(token);
            }
        }
        if (tokens.size() > 1) {
            return true;
        }
    }
    return false;
}
int main() {
    auto candidate = f;
    assert(candidate(("only one line"), (" ")) == (true));
}

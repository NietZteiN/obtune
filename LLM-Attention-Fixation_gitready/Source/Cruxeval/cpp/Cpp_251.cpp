#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::vector<std::vector<std::string>> messages) {
    std::string phone_code = "+353";
    std::vector<std::string> result;
    for (auto& message : messages) {
        for (auto& ch : phone_code) {
            message.push_back(std::string(1, ch));
        }
        result.push_back(message[0]);
        for (size_t i = 1; i < message.size(); ++i) {
            result.back() += ";" + message[i];
        }
    }
    std::string final_result = result[0];
    for (size_t i = 1; i < result.size(); ++i) {
        final_result += ". " + result[i];
    }
    return final_result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::vector<std::string>>({(std::vector<std::string>)std::vector<std::string>({(std::string)"Marie", (std::string)"Nelson", (std::string)"Oscar"})}))) == ("Marie;Nelson;Oscar;+;3;5;3"));
}

#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> items) {
    std::vector<std::string> result;
    for (const std::string& item : items) {
        for (char d : item) {
            if (!isdigit(d)) {
                result.push_back(std::string(1, d));
            }
        }
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"123", (std::string)"cat", (std::string)"d dee"}))) == (std::vector<std::string>({(std::string)"c", (std::string)"a", (std::string)"t", (std::string)"d", (std::string)" ", (std::string)"d", (std::string)"e", (std::string)"e"})));
}

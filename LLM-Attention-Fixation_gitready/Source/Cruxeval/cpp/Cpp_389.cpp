#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> total, std::string arg) {
    if (arg.find('[') != std::string::npos) {
        for (char c : arg) {
            if (isalpha(c)) {
                total.push_back(std::string(1, c));
            }
        }
    } else {
        for (char c : arg) {
            total.push_back(std::string(1, c));
        }
    }
    return total;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"1", (std::string)"2", (std::string)"3"})), ("nammo")) == (std::vector<std::string>({(std::string)"1", (std::string)"2", (std::string)"3", (std::string)"n", (std::string)"a", (std::string)"m", (std::string)"m", (std::string)"o"})));
}

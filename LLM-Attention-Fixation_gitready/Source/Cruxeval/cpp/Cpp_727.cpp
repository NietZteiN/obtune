#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> numbers, std::string prefix) {
    std::vector<std::string> result;
    for (const std::string& n : numbers) {
        if (n.size() > prefix.size() && n.substr(0, prefix.size()) == prefix) {
            result.push_back(n.substr(prefix.size()));
        } else {
            result.push_back(n);
        }
    }
    std::sort(result.begin(), result.end());
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"ix", (std::string)"dxh", (std::string)"snegi", (std::string)"wiubvu"})), ("")) == (std::vector<std::string>({(std::string)"dxh", (std::string)"ix", (std::string)"snegi", (std::string)"wiubvu"})));
}

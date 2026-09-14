#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::string test, std::string sep, long maxsplit) {
    try {
        std::vector<std::string> result;
        size_t pos = 0;
        size_t found;
        while ((found = test.find_first_of(sep, pos)) != std::string::npos) {
            result.push_back(test.substr(pos, found - pos));
            pos = found + sep.size();
            if (result.size() == maxsplit) {
                break;
            }
        }
        result.push_back(test.substr(pos));
        return result;
    } catch (...) {
        std::vector<std::string> result;
        size_t pos = 0;
        size_t found;
        while ((found = test.find_first_of(' ', pos)) != std::string::npos) {
            result.push_back(test.substr(pos, found - pos));
            pos = found + 1;
        }
        result.push_back(test.substr(pos));
        return result;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("ab cd"), ("x"), (2)) == (std::vector<std::string>({(std::string)"ab cd"})));
}

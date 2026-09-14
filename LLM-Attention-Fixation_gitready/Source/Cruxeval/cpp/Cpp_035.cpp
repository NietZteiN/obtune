#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::string pattern, std::vector<std::string> items) {
    std::vector<long> result;
    for (const std::string& text : items) {
        size_t pos = text.rfind(pattern);
        if (pos != std::string::npos) {
            result.push_back(pos);
        }
    }
    
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((" B "), (std::vector<std::string>({(std::string)" bBb ", (std::string)" BaB ", (std::string)" bB", (std::string)" bBbB ", (std::string)" bbb"}))) == (std::vector<long>()));
}

#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(long number) {
    std::vector<std::string> result;
    std::map<char, int> transl = {{'A', 1}, {'B', 2}, {'C', 3}, {'D', 4}, {'E', 5}};
    
    for (auto const& pair : transl) {
        if (pair.second % number == 0) {
            result.push_back(std::string(1, pair.first));
        }
    }
    
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((2)) == (std::vector<std::string>({(std::string)"B", (std::string)"D"})));
}

#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::string s, std::vector<long> characters) {
    std::vector<std::string> result;
    for (long i : characters) {
        result.push_back(s.substr(i, 1));
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("s7 6s 1ss"), (std::vector<long>({(long)1, (long)3, (long)6, (long)1, (long)2}))) == (std::vector<std::string>({(std::string)"7", (std::string)"6", (std::string)"1", (std::string)"7", (std::string)" "})));
}

#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<std::string> li) {
    std::vector<long> result;
    for (const auto& i : li) {
        result.push_back(std::count(li.begin(), li.end(), i));
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"k", (std::string)"x", (std::string)"c", (std::string)"x", (std::string)"x", (std::string)"b", (std::string)"l", (std::string)"f", (std::string)"r", (std::string)"n", (std::string)"g"}))) == (std::vector<long>({(long)1, (long)3, (long)1, (long)3, (long)3, (long)1, (long)1, (long)1, (long)1, (long)1, (long)1})));
}

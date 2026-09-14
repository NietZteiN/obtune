#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::string text, std::string sub) {
    std::vector<long> index;
    size_t starting = 0;
    while (starting != std::string::npos) {
        starting = text.find(sub, starting);
        if (starting != std::string::npos) {
            index.push_back(starting);
            starting += sub.length();
        }
    }
    return index;
}
int main() {
    auto candidate = f;
    assert(candidate(("egmdartoa"), ("good")) == (std::vector<long>()));
}

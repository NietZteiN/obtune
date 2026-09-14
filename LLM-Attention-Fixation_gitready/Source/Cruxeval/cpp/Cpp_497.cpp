#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(long n) {
    std::vector<std::string> b;
    std::string numStr = std::to_string(n);
    for (int i = 0; i < numStr.length(); ++i) {
        b.push_back(std::string(1, numStr[i]));
    }
    for (int i = 2; i < b.size(); ++i) {
        b[i] += '+';
    }
    return b;
}
int main() {
    auto candidate = f;
    assert(candidate((44)) == (std::vector<std::string>({(std::string)"4", (std::string)"4"})));
}

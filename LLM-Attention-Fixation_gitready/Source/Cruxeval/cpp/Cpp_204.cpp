#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::string name) {
    return {std::string(1, name[0]), std::string(1, name[1])};
}
int main() {
    auto candidate = f;
    assert(candidate(("master. ")) == (std::vector<std::string>({(std::string)"m", (std::string)"a"})));
}

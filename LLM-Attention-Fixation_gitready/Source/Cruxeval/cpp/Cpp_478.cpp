#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::string sb) {
    std::map<std::string, long> d;
    for (char s : sb) {
        d[std::string(1, s)] = d[std::string(1, s)] + 1;
    }
    return d;
}
int main() {
    auto candidate = f;
    assert(candidate(("meow meow")) == (std::map<std::string,long>({{"m", 2}, {"e", 2}, {"o", 2}, {"w", 2}, {" ", 1}})));
}

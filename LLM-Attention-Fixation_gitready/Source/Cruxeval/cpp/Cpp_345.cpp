#include<assert.h>
#include<bits/stdc++.h>
std::tuple<std::string, std::string> f(std::string a, std::string b) {
    if (a < b) {
        return std::make_tuple(b, a);
    }
    return std::make_tuple(a, b);
}
int main() {
    auto candidate = f;
    assert(candidate(("ml"), ("mv")) == (std::make_tuple("mv", "ml")));
}

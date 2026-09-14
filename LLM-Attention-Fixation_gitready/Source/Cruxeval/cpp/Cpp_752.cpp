#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, long amount) {
    return std::string(std::max(0L, amount - static_cast<long>(s.length())), 'z') + s;
}
int main() {
    auto candidate = f;
    assert(candidate(("abc"), (8)) == ("zzzzzabc"));
}

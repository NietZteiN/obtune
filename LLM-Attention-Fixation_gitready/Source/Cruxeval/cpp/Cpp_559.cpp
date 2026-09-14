#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string n) {
    std::replace(n.begin()+1, n.end(), '-', '_');
    return n.substr(0, 1) + '.' + n.substr(1);
}
int main() {
    auto candidate = f;
    assert(candidate(("first-second-third")) == ("f.irst_second_third"));
}

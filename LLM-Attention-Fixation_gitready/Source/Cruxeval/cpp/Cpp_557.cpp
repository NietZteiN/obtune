#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s) {
    std::string d = s.substr(0, s.rfind("ar"));
    return d + " ar " + s.substr(d.length() + 2);
}
int main() {
    auto candidate = f;
    assert(candidate(("xxxarmmarxx")) == ("xxxarmm ar xx"));
}

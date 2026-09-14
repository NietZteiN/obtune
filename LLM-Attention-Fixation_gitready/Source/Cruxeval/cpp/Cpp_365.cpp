#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string n, std::string s) {
    if(s.find(n) == 0){
        size_t pos = s.find(n);
        std::string pre = s.substr(0, pos);
        return pre + n + s.substr(pos + n.length());
    }
    return s;
}
int main() {
    auto candidate = f;
    assert(candidate(("xqc"), ("mRcwVqXsRDRb")) == ("mRcwVqXsRDRb"));
}

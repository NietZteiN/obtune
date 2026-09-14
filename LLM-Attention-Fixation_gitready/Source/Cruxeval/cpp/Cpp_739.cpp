#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string st, std::vector<std::string> pattern) {
    for (const std::string& p : pattern) {
        if (st.find(p) != 0) {
            return false;
        }
        st = st.substr(p.length());
    }
    return true;
}
int main() {
    auto candidate = f;
    assert(candidate(("qwbnjrxs"), (std::vector<std::string>({(std::string)"jr", (std::string)"b", (std::string)"r", (std::string)"qw"}))) == (false));
}

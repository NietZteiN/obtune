#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string st) {
    if (st[0] == '~') {
        std::string e = std::string(10 - st.size(), 's') + st;
        return f(e);
    } else {
        return std::string(10 - st.size(), 'n') + st;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("eqe-;ew22")) == ("neqe-;ew22"));
}

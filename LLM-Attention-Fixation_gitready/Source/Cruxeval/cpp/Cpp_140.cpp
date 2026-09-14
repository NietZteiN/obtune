#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string st) {
    if (st.substr(0, st.find_last_of('h') + 1) >= st.substr(0, st.find_last_of('i') + 1)) {
        return "Hey";
    } else {
        return "Hi";
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("Hi there")) == ("Hey"));
}

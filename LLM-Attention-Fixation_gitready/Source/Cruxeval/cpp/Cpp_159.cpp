#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string st) {
    std::reverse(st.begin(), st.end());
    for (int i = 0; i < st.length(); i++) {
        if (islower(st[i]))
            st[i] = toupper(st[i]);
        else if (isupper(st[i]))
            st[i] = tolower(st[i]);
    }
    return st;
}
int main() {
    auto candidate = f;
    assert(candidate(("RTiGM")) == ("mgItr"));
}

#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string a, std::string b, std::string c, std::string d) {
    return a.empty() ? c.empty() ? "" : d : b;
}
int main() {
    auto candidate = f;
    assert(candidate(("CJU"), ("BFS"), ("WBYDZPVES"), ("Y")) == ("BFS"));
}

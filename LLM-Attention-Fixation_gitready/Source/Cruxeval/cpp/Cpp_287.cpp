#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string name) {
    if(std::all_of(name.begin(), name.end(), ::islower)) {
        std::transform(name.begin(), name.end(), name.begin(), ::toupper);
    } else {
        std::transform(name.begin(), name.end(), name.begin(), ::tolower);
    }
    return name;
}
int main() {
    auto candidate = f;
    assert(candidate(("Pinneaple")) == ("pinneaple"));
}

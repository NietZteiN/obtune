#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string string) {
    if (string.substr(0, 4) != "Nuva") {
        return "no";
    } else {
        return string;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("Nuva?dlfuyjys")) == ("Nuva?dlfuyjys"));
}

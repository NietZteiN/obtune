#include<assert.h>
#include<bits/stdc++.h>
std::tuple<std::string, std::string> f(std::map<std::string,long> c, long st, long ed) {
    std::map<long, std::string> d;
    std::string a, b;
    for(auto const& pair : c) {
        d[pair.second] = pair.first;
        if(pair.second == st) {
            a = pair.first;
        }
        if(pair.second == ed) {
            b = pair.first;
        }
    }
    std::string w = d[st];
    return (a > b) ? std::make_tuple(w, b) : std::make_tuple(b, w);
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"TEXT", 7}, {"CODE", 3}})), (7), (3)) == (std::make_tuple("TEXT", "CODE")));
}

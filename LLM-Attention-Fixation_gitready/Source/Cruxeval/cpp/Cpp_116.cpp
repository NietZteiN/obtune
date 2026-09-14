#include<assert.h>
#include<bits/stdc++.h>
std::map<long,long> f(std::map<long,long> d, long count) {
    for(long i = 0; i < count; i++){
        if(d.empty()) {
            break;
        }
        d.erase(std::prev(d.end()));
    } 
    return d;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>()), (200)) == (std::map<long,long>()));
}

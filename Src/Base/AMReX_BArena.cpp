#include <AMReX_BArena.H>

void*
amrex::BArena::alloc (std::size_t sz_)
{
    return std::aligned_alloc(64,sz_);
}

void
amrex::BArena::free (void* pt)
{
    std::free(pt);
}

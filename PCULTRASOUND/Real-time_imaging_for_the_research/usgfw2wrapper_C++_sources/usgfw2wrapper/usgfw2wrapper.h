///////////////////////////////////////////////////////////
//#include <initguid.h>
#include <dshow.h>
#include "qedit_custom.h"
#include <windows.h>
#include "strmif.h"
#include "Usgfw2_h.h"
#include "Usgfw2_i.c"
#include "resource.h"

#define SAFE_RELEASE(x) { if (x) x->Release(); x = NULL; }

#ifdef __cplusplus
extern "C" {
#endif

int init_ultrasound_usgfw2();
int find_connected_probe();
int data_view_function();
int mixer_control_function(int left, int top, int right, int bottom, int R, int G, int B);
void return_pixel_values(unsigned int*);
void CreateUsgControl(IUsgDataView* data_view, const IID* type_id, ULONG scan_mode, ULONG stream_id, void** ctrl);
void get_resolution(float* delta_x_cm, float* delta_y_cm);
void Freeze_ultrasound_scanning(); 
void Run_ultrasound_scanning();
void Close_and_release(); 
void ReleaseUsgControls();
void on_init();
void Stop_ultrasound_scanning();

#ifdef __cplusplus
} // closing brace for extern "C"
#endif

IUsgfw2* m_usgfw2;			                    // main Usgfw2 library object
IProbe* probe;									// current probe
HRESULT hr = S_OK;
IUsgDataView* data_view;                        // data view from probe
IUsgDataView* m_data_view;						// data view from probe
IUsgScanMode* mode;                             // scan mode
IUsgMixerControl* mixer_control;				// B mixer control
IUsgImageProperties* image_properties_b;		// B image properties




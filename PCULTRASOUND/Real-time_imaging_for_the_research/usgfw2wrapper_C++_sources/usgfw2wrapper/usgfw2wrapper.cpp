#include "stdafx.h"
#include "math.h"
#include "usgfw2wrapper.h"
#include <conio.h>
#include "DIBSectn.h"
//#include <resource.h>
#include "UsgfwWindow.h"

CUsgfwWindow* p_wnd;
HWND hWnd; // ultrasound output window

BOOL APIENTRY DllMain( HANDLE hModule, 
                       DWORD  ul_reason_for_call, 
                       LPVOID lpReserved
					 )
{
	if (ul_reason_for_call == DLL_PROCESS_ATTACH)
		CUsgfwWindow::RegisterClass((HINSTANCE)hModule);

	return TRUE;
}

void on_init()
{
	m_usgfw2 = NULL;
	probe = NULL;									
	hWnd = NULL;
    hr = S_OK;
    data_view = NULL;
    m_data_view = NULL;						
    mode = NULL; 
    mixer_control = NULL;				
	image_properties_b = NULL;	
	p_wnd = NULL;
}


int init_ultrasound_usgfw2()
{	
	CoInitialize(NULL);			
	hr = CoCreateInstance(CLSID_Usgfw2, NULL, CLSCTX_INPROC_SERVER, IID_IUsgfw2, (LPVOID*)&m_usgfw2);
	if (hr != S_OK)
	{
		m_usgfw2 = NULL;
		return 2;
	} 
	else
	{
	return 3;
	}
}

int find_connected_probe()
{
        IUnknown* tmp_obj = NULL;
	    IUsgCollection* probes_collection = NULL;
 			
		// get collection of connected probes
		m_usgfw2->get_ProbesCollection(&tmp_obj);
		
		if (tmp_obj == NULL)
		{
			probes_collection = NULL;
			return 4;
		}

		hr = tmp_obj->QueryInterface(IID_IUsgCollection,(void**)&probes_collection);
		tmp_obj->Release();
		if ( (hr != S_OK) || (probes_collection == NULL) )
		{
			probes_collection = NULL;
			return 5;
		}

		// get the number of connected probes
		LONG probes_count = 0;
		probes_collection->get_Count(&probes_count);
		if (probes_count == 0)
		{
			probes_collection->Release();
			probes_collection = NULL;
			return 6;
		}

		tmp_obj = NULL;
		probes_collection->Item(0,&tmp_obj); // get first available probe
		probes_collection->Release();
		probes_collection = NULL;
		
		if (tmp_obj == NULL)
		{
			probe = NULL;
			return 7;
		}
		hr = tmp_obj->QueryInterface(IID_IProbe,(void**)&probe);
		tmp_obj->Release();
		
		if ( (hr != S_OK) || (probe == NULL) )
		{
			probe = NULL;
			return 8;
		}
		else
		{
		return 101;
		}
}

int data_view_function()
{
	    // create main ultrasound scanning object for selected probe
		m_usgfw2->CreateDataView(probe, &data_view);

		if (data_view == NULL)
		{
			return -99;
		}

		m_data_view = NULL;
        data_view->QueryInterface(IID_IUsgDataView, (void**)&m_data_view);
		if (m_data_view == NULL)
			return -150;

		m_data_view->put_ScanState(SCAN_STATE_STOP);
		

		mode = NULL;
		m_data_view->GetScanModeObj(SCAN_MODE_B,&mode);
		if (mode == NULL)
		{
			return -100;
		}
		else
		{
		    return 100;
		}
}

void get_resolution(float* delta_x_cm, float* delta_y_cm)
{
    tagImageResolution resolution;
	image_properties_b->GetResolution(&resolution, 0);
    	
	*delta_x_cm = 1000/((float)resolution.nYPelsPerUnit);
	*delta_y_cm = 1000/((float)resolution.nXPelsPerUnit);
}


void CreateUsgControl(IUsgDataView* data_view, const IID& type_id, ULONG scan_mode, ULONG stream_id, void** ctrl)
{
	IUsgControl* ctrl2;
	ctrl2 = NULL;

	if (data_view == NULL) return;

	data_view->GetControlObj(&type_id, scan_mode, stream_id, &ctrl2);

	if (ctrl2 != NULL)
	{
		HRESULT hr;
		hr = ctrl2->QueryInterface(type_id, (void**)ctrl);
		if (hr != S_OK)
			*ctrl = NULL;
		SAFE_RELEASE(ctrl2);		
	}
}

int mixer_control_function(int left, int top, int right, int bottom, int R, int G, int B)
{
       
       
	   p_wnd = new CUsgfwWindow();	   
	   hWnd = NULL;
	   hWnd = p_wnd->Create(L"Usgfw2Imaging", 0, 0, 0, (right-left), (bottom-top), NULL, 0, 0);    	   
	   
	   do
	   {

        mixer_control = NULL;
		// get B mixer control //
		mode->GetMixerControl(SCAN_MODE_B,0,&mixer_control);
		mode->Release();
		mode = NULL;
		if (mixer_control == NULL)
		{
			return -97;
		}

		// set B scanning mode
		m_data_view->put_ScanMode(SCAN_MODE_B);
		mixer_control->SetOutputWindow((long)hWnd);

		tagRECT rect1;
		rect1.left		= left;
		rect1.top		= top;
		rect1.right		= right;
		rect1.bottom	= bottom;

		// set B ultrasound output rectangle
		mixer_control->SetOutputRect(&rect1);

		// set background color that surrounds B ultrasound image
		tagPALETTEENTRY clr1;
		clr1.peRed		= R;
		clr1.peGreen	= G;
		clr1.peBlue		= B;
		clr1.peFlags	= 0;
		mixer_control->put_BkColor(clr1);
       
		m_data_view->put_ScanState(SCAN_STATE_RUN);

		// image properties B for obtaining pixel size - Resolution
		IUnknown* tmp_obj = NULL;
		CreateUsgControl(m_data_view, IID_IUsgImageProperties, SCAN_MODE_B, 0, (void**)&tmp_obj);
		if (tmp_obj != NULL)
			image_properties_b = (IUsgImageProperties*)tmp_obj;
		else
			image_properties_b = NULL;
		
	   tmp_obj->Release();
	   
	   return 89;

	} while (false); 
}
void return_pixel_values(unsigned int* color)
{
	
    HDC hdc;
	HDC hdc1;
    hdc = CreateCompatibleDC(NULL);
    hdc1 = CreateCompatibleDC(hdc);
	HBITMAP hbitmap_handle = NULL;
	
	mixer_control->GetCurrentBitmap((LONG*)&hbitmap_handle);
     
	LPBITMAPINFO pbmi;
	pbmi = DSGetBITMAPINFOForDIBSection(hbitmap_handle);


    SelectObject(hdc1, hbitmap_handle);
	    
    BYTE* bitPointer = NULL;
	
    BITMAPINFO bitmap;
    ZeroMemory(&bitmap, sizeof(BITMAPINFO));
    bitmap.bmiHeader.biSize = pbmi->bmiHeader.biSize;
    bitmap.bmiHeader.biWidth = pbmi->bmiHeader.biWidth;
    bitmap.bmiHeader.biHeight = pbmi->bmiHeader.biHeight;
    bitmap.bmiHeader.biPlanes = pbmi->bmiHeader.biPlanes;
    bitmap.bmiHeader.biBitCount = pbmi->bmiHeader.biBitCount;
    bitmap.bmiHeader.biCompression = BI_RGB;
    bitmap.bmiHeader.biSizeImage = pbmi->bmiHeader.biSizeImage;
    bitmap.bmiHeader.biClrUsed = 0;
    bitmap.bmiHeader.biClrImportant = 0;
	
	HBITMAP hBitmap2 = CreateDIBSection(hdc, &bitmap, DIB_RGB_COLORS, (void**)(&bitPointer), NULL, NULL);
	    
	SelectObject(hdc, hBitmap2);
	BitBlt(hdc, 0, 0, bitmap.bmiHeader.biHeight, bitmap.bmiHeader.biWidth, hdc1, 0, 0, SRCCOPY);

    for (int i=0; i < bitmap.bmiHeader.biHeight*bitmap.bmiHeader.biWidth*4; i++)
	   *(color+i) = (unsigned int)*(bitPointer+i);
    	
	pbmi = NULL;
    bitPointer = NULL;
	::DeleteObject(hbitmap_handle);
	::DeleteObject(hBitmap2);
    DeleteDC(hdc);
	DeleteDC(hdc1);
}

void Freeze_ultrasound_scanning() 
{
	if (m_data_view == NULL) return;
	// freeze ultrasound scanning
	m_data_view->put_ScanState(SCAN_STATE_FREEZE);
}

void Run_ultrasound_scanning() 
{
    if (m_data_view == NULL) return;
	// run ultrasound scanning
	m_data_view->put_ScanState(SCAN_STATE_RUN);

}
void Stop_ultrasound_scanning() 
{
	m_data_view->put_ScanState(SCAN_STATE_STOP);
}	
void Close_and_release() 
{
	ReleaseUsgControls();	// release ultrasound scanning controls
}	

void ReleaseUsgControls()
{   
	
	//p_wnd->~CUsgfwWindow();
	if (p_wnd!=NULL){
	p_wnd->WndProc(WM_CLOSE,0,0);
	p_wnd = NULL;
	}

	if (m_data_view != NULL)
		m_data_view->put_ScanState(SCAN_STATE_STOP);
	if (hWnd != NULL)
		hWnd = NULL;

	SAFE_RELEASE(mixer_control);
	SAFE_RELEASE(m_data_view);
	SAFE_RELEASE(probe);
	SAFE_RELEASE(mode);
	SAFE_RELEASE(data_view)
	SAFE_RELEASE(image_properties_b);
	SAFE_RELEASE(m_usgfw2);
} 


